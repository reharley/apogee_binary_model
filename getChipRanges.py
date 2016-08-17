# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre
import matplotlib.pyplot as plt
import apogee.spec.plot as splot
import numpy as np

locationIDs, apogeeIDs = np.loadtxt('lists/binaries3.dat', unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
visit = 1
f = open('chipRanges.txt', 'w')
for i in range(len(locationIDs)):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	nvisits = header['NVISITS']
	print('Getting chip ranges of: ' + locationIDs[i] + ', ' + apogeeIDs[i] + ', nvisits: ' + str(nvisits))
	print(str(i + 1) + '/' + str(targetCount) + ' targets completed')
	spec = apread.apStar(locationID, apogeeID, ext=1, header=False)[2]
	for visit in spec:
		for chip in visit:
			print(chip)
			nan_vals_spec = np.where(chip == 0)[0]
			nan_ranges_spec = [(nan_vals_spec[i] + 1, nan_vals_spec[i+1]) for i in range(len(nan_vals_spec) - 1) if nan_vals_spec[i+1]!=nan_vals_spec[i]+1]
			print(nan_ranges_spec)
			f.write('{0}\t{1}\t{2}\t{3}\t{4}'.format(locationID, apogeeID,
														'[' + str(nan_ranges_spec[0][0]) + ',' + str(nan_ranges_spec[0][1]) + ']',
														'[' + str(nan_ranges_spec[1][0]) + ',' + str(nan_ranges_spec[1][1]) + ']',
														'[' + str(nan_ranges_spec[2][0]) + ',' + str(nan_ranges_spec[2][1]) + ']\n'))


mspec = ferre.interpolate(4500.,4.7,0.0,0.0,0.0,0.0)
nan_vals_mspec = np.where(np.isnan(mspec))[0]
nan_ranges_mspec = [(nan_vals_mspec[i] + 1, nan_vals_mspec[i+1]) for i in range(len(nan_vals_mspec) - 1) if nan_vals_mspec[i+1]!=nan_vals_mspec[i]+1]
f.write('{0}\t{1}\t{2}\t{3}\t{4}'.format('model', '\t\t\t\t',
													'[' + str(nan_ranges_mspec[0][0]) + ',' + str(nan_ranges_mspec[0][1]) + ']',
													'[' + str(nan_ranges_mspec[1][0]) + ',' + str(nan_ranges_mspec[1][1]) + ']',
													'[' + str(nan_ranges_mspec[2][0]) + ',' + str(nan_ranges_mspec[2][1]) + ']\n'))
f.write('{0}\t{1}\t{2}\t{3}\t{4}'.format('model', '\t\t\t\t',
													str(nan_ranges_mspec[0][1] - nan_ranges_mspec[0][0]),
													str(nan_ranges_mspec[1][1] - nan_ranges_mspec[1][0]),
													str(nan_ranges_mspec[2][1] - nan_ranges_mspec[2][0])))
f.close()
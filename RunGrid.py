# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import BinaryGrid as bg
import numpy as np
import apogee.tools.read as apread

locationIDs, apogeeIDs = np.loadtxt('lists/binaries2.dat', unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
f = open('lists/chi2.lis', 'w')
f.write('{0}\t{1}\t\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format('Field ID', '2MID', 'visit', 'TeffA', 'TeffB', 'Flux Ratio', 'chi2'))
for i in range(len(locationIDs)):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	nvisits = header['NVISITS']
	print('Plotting: ' + locationIDs[i] + ', ' + apogeeIDs[i] + ', nvisits: ' + str(nvisits))
	print(str(i) + '/' + str(targetCount) + ' targets completed')
	
	# Temperature values for our grid
	maxTeff = 5999.
	minTeff = 3500.
	params, visit, chi2 = bg.targetGrid(locationID, apogeeID, minTeff, maxTeff, plot=False)

	f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t\t{6}\n'.format(locationID, apogeeID, visit, round(params[0][0], 2), round(params[0][1], 2), round(params[6][1], 2), round(chi2,2 )))
f.close()
# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import matplotlib.pyplot as plt
from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer
from BFData import BFData

filename = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder2/interestingTargets.csv'
locationIDs, apogeeIDs, rangerd = np.loadtxt(filename, unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
print(targetCount, 'targets')

# stores all the BFData objects for all the interesting targets
intData = []
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	ranger = rangerd[i]
	intData.append(BFData(locationID, apogeeID, ranger))

print(intData[0].ranger)
ranger = 0.02

for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	print(locationID, apogeeID)
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
	data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')

	nvisits = header['NVISITS']
	for visit in range(1, nvisits):
		if (nvisits != 1):
			ccf = data['CCF'][0][1 + visit]
		else:
			ccf = data['CCF'][0]
		max1, max2 = getMaxPositions(ccf, ranger)
		if str(max2) != 'none':
			print('visit: ', visit)
			break
	
	print(max1, max2)

	print(calcR(ccf))
	if str(max1) != 'none':
		plt.scatter(max1, ccf[max1], color='red', s=30)
	if str(max2) != 'none':
		plt.scatter(max2, ccf[max2], color='orange', s=70)
	plt.plot(ccf, color='blue')
	plt.show()
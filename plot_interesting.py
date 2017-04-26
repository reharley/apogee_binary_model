# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import matplotlib.pyplot as plt
import BinFinderTools as bf
import apogee.tools.read as apread
from Timer import Timer
from BFData import BFData

#filename = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/interestingTargetsDualPeak.csv'
#filename = 'lists/binaries2.dat'
filename = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/kevin_candidate_list.csv'
locationIDs, apogeeIDs = np.loadtxt(filename, unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
print(targetCount, 'targets')

locationIDs, apogeeIDs = bf.removeSingle(locationIDs, apogeeIDs, 'kevin_candidate_list')
targetCount = len(locationIDs)
print(targetCount, 'targets')
plt.rcParams["figure.figsize"] = [20.0, 15.0]
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	print(locationID, apogeeID)
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
	data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')

	nvisits = header['NVISITS']
	for visit in range(0, nvisits):
		if (nvisits != 1):
			ccf = data['CCF'][0][2 + visit]
		else:
			ccf = data['CCF'][0]
		
		plt.plot(ccf + visit,label= 'Visit: '+str(1+visit))
		
		#axes = plt.gca()
		#axes.set_xlim([100,300])
		
		plt.xlabel('CCF Lag',fontsize=15)
		plt.ylabel('$\widehat{CCF}$ Units', fontsize=15)
		plt.title(' All Visits for {0} / {1}'.format(locationID, apogeeID),fontsize=16)
		plt.legend(loc='lower left')
	
	plt.show()
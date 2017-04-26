# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

#from BFData import BFData
#from BinPlot import *
from BinFinderTools import getAllTargets, recordTargetsCSV
import numpy as np

print('hello')
folder = "/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder_Plots/hist/non/"
apogeeIDs, locationIDs = getAllTargets()
targetCount = len(apogeeIDs)

filename = 'lists/Binary_Results_EVP1-4_Rmax.csv'
apogeeIDs2 = np.loadtxt(filename, delimiter=',', unpack=True, dtype=str,skiprows=1)
apogeeIDs = np.array(apogeeIDs)
locationIDs = np.array(locationIDs)
count = len(apogeeIDs2[0])
intersectAp = []
missingAp = []
for i in range(count):
	locationIDs2 = locationIDs[np.argwhere(apogeeIDs == apogeeIDs2[0][i])]
	for id in locationIDs2:
		intersectAp.append([id[0], apogeeIDs2[0][i]])
	if len(locationIDs2) == 0:
		missingAp.append(['n/a', apogeeIDs2[0][i]])
	
recordTargetsCSV(intersectAp, 'kevin_candidate_list')
recordTargetsCSV(missingAp, 'kevin_candidate_list_missing')
count = len(locationIDs)
interestingTargets = []

'''count = 0
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	recorded = False
	targetCount = len(locationIDs)
	data = []

	if count > 1000:
		recordTargetsCSV(data, 'singles')
		break
	elif (BFData.exists(locationID, apogeeID)):
		if (BFData(locationID, apogeeID).secondPeak() is True):
			data.append([locationID, apogeeID])
			count = count + 1
			print(count)'''
print('done')
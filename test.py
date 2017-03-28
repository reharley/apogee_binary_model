# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinPlot import *
from BinFinderTools import *

folder = "/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder_Plots/hist/non/"
apogeeIDs, locationIDs = getAllTargets()
targetCount = len(apogeeIDs)

count = len(locationIDs)
interestingTargets = []

otherCount = 0
tCount = 2000
for j in range(20):
	r = np.zeros(tCount)
	for i in range(tCount):
		locationID = locationIDs[i]
		apogeeID = apogeeIDs[i]
		recorded = False
		
		try:
			bf = BFData(locationID, apogeeID, .02)
			r[i] = bf.lowestR(j)
		except:
			r[i] = -1.0
			continue
		

		plt.hist(r, bins=25)
		plt.xlabel('r')
		plt.ylabel('N')
		plt.title('R' + str(j), loc='left')
		plt.savefig(folder + 'r' + str(j) + '.png', format='png')
		plt.close()

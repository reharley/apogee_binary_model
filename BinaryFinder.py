# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer

data = apread.allStar(dr='13')
apogeeIDs = data['APOGEE_ID']
locationIDs = data['LOCATION_ID']
targetCount = len(apogeeIDs)

t = Timer()

t.start()
interestingTargets = []
skippedTargets = []
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	recorded = False
	for k in range(2, 50):
		ranger = k / 100.

		try:
			badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
			data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
		except IOError:
			skippedTargets.append([locationID, apogeeID])
			break
		nvisits = header['NVISITS']

		positions = []
		for visit in range(1, nvisits):
			if (nvisits != 1):
				ccf = data['CCF'][0][1 + visit]
			else:
				ccf = data['CCF'][0]
			max1, max2 = getMaxPositions(ccf, ranger)

			r = []
			for cut in range(20):
				r.append(calcR(ccf, cut*10, (401 - (cut * 10))))
			
			if r < 1.0:
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, "r"])

			if str(max2) != 'none':
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, ranger])

			positions.append([max1, max2, r])
		
		reportPositions(locationID, apogeeID, ranger, positions)

recordTargets(interestingTargets, ranger, 'interestingTargets')
recordTargets(skippedTargets, ranger, 'skippedTargets')

print("done", t.current())
t.end()
# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer

# Get all Targets
apogeeIDs, locationIDs = getAllTargets()
targetCount = len(apogeeIDs)

t = Timer()

t.start()
interestingTargets = []
skippedTargets = []
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	recorded = False

	# Get fits files
	try:
		badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
		data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
	except IOError:
		skippedTargets.append([locationID, apogeeID])
		continue
	
	#calculate r and test for second peak
	for k in range(1, 50):
		ranger = k / 100.
		nvisits = header['NVISITS']

		positions = []
		for visit in range(1, nvisits):
			if (nvisits != 1):
				ccf = data['CCF'][0][1 + visit]
			else:
				ccf = data['CCF'][0]
			max1, max2 = getMaxPositions(ccf, ranger)

			# Calculate r values
			r = []
			for cut in range(20):
				r.append(calcR(ccf, cut*10, (401 - (cut * 10))))
			
			if r < 7.0:
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, "r"])

			if str(max2) != 'none':
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, ranger])

			positions.append([max1, max2, r])
		
		reportPositions(locationID, apogeeID, ranger, positions)

recordTargets(interestingTargets, 'interestingTargets')
recordTargets(skippedTargets, 'skippedTargets')

print("done", t.current())
t.end()
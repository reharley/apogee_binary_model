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
		for visit in range(0, nvisits):
			if (nvisits != 1):
				ccf = data['CCF'][0][2 + visit]
			else:
				ccf = data['CCF'][0]
			max1, max2 = getMaxPositions(ccf, ranger)

			# Calculate r values
			r = []

			# calculate r by reflecting about the highest peak
			ccfCount = len(ccf)
			if str(max2) != np.nan:
				peakLoc = max(max1, max2)
			else:
				peakLoc = max1

			try:
				if (ccfCount > peakLoc*2):
					r.append(calcR(ccf, pos2=peakLoc*2, peakLoc=peakLoc))
				else:
					r.append(calcR(ccf, pos1=2*peakLoc-ccfCount+1, pos2=ccfCount-1, peakLoc=peakLoc))
			except:
				r.append(np.nan)
				print(locationID, apogeeID)
			
			# calculate r by reflecting about the center (201)
			for cut in range(20):
				r.append(calcR(ccf, pos1=cut*10+1, pos2=(401 - (cut * 10)), peakLoc=201))

			if r < 7.0:
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, "r"])

			if np.isnan(max2) is False:
				if recorded is False:
					recorded = True
					interestingTargets.append([locationID, apogeeID, ranger])
			elif recorded is True:
				#record when the binary is no longer detected
				currentLen = len(interestingTargets)
				interestingTargets[currentLen - 1].append(ranger)

			positions.append([max1, max2, r])
		
		reportPositions(locationID, apogeeID, ranger, positions)

recordTargets(interestingTargets, 'interestingTargets')
recordTargets(skippedTargets, 'skippedTargets')

print("done", t.current())
t.end()
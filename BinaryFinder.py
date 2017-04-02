# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer

# Get all Targets
apogeeIDs, locationIDs = getAllTargets()
targetCount = len(locationIDs)

t = Timer()
t.start()
interestingTargetsr = []
interestingTargetsDualPeak = []
skippedTargets = []
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]

	# Get fits files
	try:
		badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='12', header=True)
		data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='12')
	except IOError:
		skippedTargets.append([locationID, apogeeID])
		continue
	
	# Calculate r and test for second peak
	nvisits = header['NVISITS']

	positions = []
	for visit in range(0, nvisits):
		if (nvisits != 1):
			ccf = data['CCF'][0][2 + visit]
		else:
			ccf = data['CCF'][0]
		max1, max2, peakhDiff = getMaxPositions(ccf)
		
		# Calculate r values
		r = []

		# Calculate r by reflecting about the highest peak
		ccfCount = len(ccf)
		if max2 != np.nan:
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
		
		if r[0] < 7.0:
			interestingTargetsr.append([locationID, apogeeID])

		if np.isnan(max2) == False:
			interestingTargetsDualPeak.append([locationID, apogeeID])

		positions.append([max1, max2, peakhDiff, r])
	
	reportPositions(locationID, apogeeID, positions)

recordTargets(interestingTargetsr, 'interestingTargetsr')
recordTargets(interestingTargetsDualPeak, 'interestingTargetsDualPeak')
recordTargets(skippedTargets, 'skippedTargets')

print("done", t.current())
t.end()
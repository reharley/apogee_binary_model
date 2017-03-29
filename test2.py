# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer


locationID = 4477
apogeeID = '2M01220226+1745349'
ranger = 0.01
print(locationID, apogeeID)
badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')

nvisits = header['NVISITS']
for visit in range(0, nvisits):
	if (nvisits != 1):
		ccf = data['CCF'][0][2 + visit]
	else:
		ccf = data['CCF'][0]
	max1, max2 = getMaxPositions(ccf, ranger)
	
	# calculate r by reflecting about the highest peak
	ccfCount = len(ccf)
	if str(max2) != np.nan:
		peakLoc = max(max1, max2)
	else:
		peakLoc = max1
	
	print('visit', visit+1, peakLoc, max1, max2)
	if (ccfCount > peakLoc*2):
		print(calcR(ccf, pos2=peakLoc*2, peakLoc=peakLoc))
	else:
		print(calcR(ccf, pos1=2*peakLoc-ccfCount+1, pos2=ccfCount-1, peakLoc=peakLoc))
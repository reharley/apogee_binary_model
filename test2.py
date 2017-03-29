# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer

locationID = 4590
apogeeID = '2M00092179+0038065'
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
	if str(max2) != 'none':
		ccfCenter = max(max1, max2)
	else:
		ccfCenter = max1
	
	print('visit', visit)
	if (ccfCount > ccfCenter*2):
		print(calcR(ccf, pos2=ccfCenter*2, ccfCenter=ccfCenter))
	else:
		print(calcR(ccf, pos1=2*ccfCenter-ccfCount+1, pos2=ccfCount-1, ccfCenter=ccfCenter))
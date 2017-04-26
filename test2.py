# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()


import apogee.tools.read as apread
from Timer import Timer
from BFData import BFData
import matplotlib.pyplot as plt
import numpy as np
import BinFinderTools as bf

locationID = 4424
apogeeID = '2M00071354+5804306'
ranger = 0.01
print(locationID, apogeeID)
badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
other = BFData(locationID, apogeeID)
print(other.peakhDiff, other.max2, other.max1)
print(np.array(other.max2)-np.array(other.max1), other.deltaR())
nvisits = header['NVISITS']
print(nvisits)
for visit in range(0, nvisits):
	if (nvisits != 1):
		ccf = data['CCF'][0][2 + visit]
		print(header['SNRVIS' + str(1	+visit)])
	else:
		ccf = data['CCF'][0]
		print(header['SNRVIS1'])
	print(bf.getMaxPositions(ccf))
	plt.plot(ccf + visit,label= 'Visit: '+str(1+visit))
plt.show()
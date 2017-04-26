# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import matplotlib.pyplot as plt
import apogee.tools.read as apread
from BinFinderTools import *


#smudge star (raptor star, fast rotator) ('4217', '2M01033978+8436248')
#binary 4587, '2M03285425+3037402'
#
locationID = 4217
apogeeID = '2M01033978+8436248'
print(locationID, apogeeID)
badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')

nvisits = header['NVISITS']
for visit in range(0, nvisits):
	if (nvisits != 1):
		# first 2 are not ccfs for individual visits
		ccf = data['CCF'][0][2 + visit]
	else:
		ccf = data['CCF'][0]
	
	max1, max2, peakhDiff = getMaxPositions(ccf)
	print(peakhDiff)
	r = calcR(ccf, pos1=1)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.set_title('Fast Rotator {0}/{1} Visit: {2}'.format(locationID, apogeeID, visit+1))
	ax.set_ylabel('Agreement')
	ax.set_xlabel('CCF Lag')
	ax.text(0.25, 0.9, 'R: {0}\nPeak HDiff: {1}'.format(round(r, 2), round(peakhDiff, 4)),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes)
	ax.plot(ccf, color='blue')
	plt.savefig('plots/figure.png', format='png', dpi=300)

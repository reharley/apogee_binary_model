# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import apogee.tools.read as apread

locationIDs, apogeeIDs = np.loadtxt('lists/test_list.dat', unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
for i in range(len(locationIDs)):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	sumData = apread.allVisit(raw=True, ext=1)
	indexData = apread.allVisit(raw=True, ext=2)
	data = apread.apVisit(apogeeID, header=False)
	print(data[0])
	index = np.where(sumData['APOGEE_ID'] == apogeeID)

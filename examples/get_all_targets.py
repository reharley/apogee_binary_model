import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread

data = apread.allStar(dr='13')
apogeeIDs = data['APOGEE_ID']
locationIDs = data['LOCATION_ID']
targetCount = len(apogeeIDs)
filename = 'lists/all.csv'
f = open(filename, 'w')

for i in range(targetCount):
	f.write(str(locationIDs[i]) + ',' + str(apogeeIDs[i]) + '\n')
f.close()
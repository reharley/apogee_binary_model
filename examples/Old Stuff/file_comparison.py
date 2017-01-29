import numpy as np


ranger = 0.25
filename = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder/' + str(ranger) + '/interestingTargets.csv'
locationIDs, apogeeIDs = np.loadtxt(filename, unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
data1 = np.loadtxt('/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/DR13_Rmin_XR_Max.lis', skiprows=1, unpack=True, dtype=str)

f = open('jessJess.csv', 'w')
f.write('{0},{1},{2},{3}\n'.format('fieldID', 'apogeeID', 'r','x_ranges'))
for i in range(targetCount):
	apogeeID = apogeeIDs[i]
	locationID = locationIDs[i]
	row = np.where(np.logical_and(data1[1] == apogeeID, data1[0] == locationID))
	try:
		if(len(row) != 0):
			f.write('{0},{1},{2},{3}\n'.format(locationID, apogeeID, data1[2][row][0], data1[4][row][0]))
	except:
		continue
f.close()
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import numpy as np
import os

def findInflection(x):
	maxPos = np.argmax(x)
	pos1, pos2 = -1, -1
	for i in range(maxPos, len(x) - 1):
		if(x[i + 1] - x[i] > 0):
			pos1 = i
			break
	for i in range(maxPos, 1, -1):
		if(x[i - 1] - x[i] > 0):
			pos2 = i
			break
	return pos2, pos1

def getMaxPositions(x, yBufferRange):
	temp = np.array(x)
	max1 = np.nanargmax(x)
	pos1, pos2 = findInflection(temp)
	temp[pos1:pos2] = np.nan
	temp[np.where(temp < 0.1)] = np.nan
	try:
		max2 = np.nanargmax(temp)
		if (max2 - pos1 < max2 - pos2):
			if (x[max2] - x[pos1] > yBufferRange):
				max2 = 'none'
		elif (max2 - pos1 > max2 - pos2):
			if (x[max2] - x[pos2] > yBufferRange):
				max2 = 'none'
	except ValueError:
		max2 = 'none'
	return max1, max2

def reportPositions(locationID, apogeeID, positions):
	visitCount = len(positions)
	
	if not os.path.exists('lists/binaryTest/' + str(locationID) + '/'):
		os.makedirs('lists/binaryTest/' + str(locationID) + '/')
	filename = 'lists/binaryTest/' + str(locationID) + '/' + str(apogeeID) + '.tbl'
	f = open(filename, 'w')
	
	f.write('visit\tmax1\tmax2\n')
	for i in range(visitCount):
		f.write(str(i+1) + '\t' + str(positions[i][0]) + '\t' + str(positions[i][1]) + '\n')
	f.close()

def reportTargets(targets, filename):
	targetCount = len(targets)
	
	if not os.path.exists('lists/'):
		os.makedirs('lists/')
	filename = 'lists/' + filename + '.csv'
	f = open(filename, 'w')
	
	for i in range(targetCount):
		f.write(str(targets[0]) + ',' + str(targets[1]) + '\n')
	f.close()

data = apread.allStar(dr='13')
apogeeIDs = data['APOGEE_ID']
locationIDs = data['LOCATION_ID']

targetCount = len(apogeeIDs)
interestingTargets = []
skippedTargets = []
for i in range(targetCount):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	try:
		badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13',header=True)
	except IOError:
		skippedTargets.append([locationID, apogeeID])
		continue
	nvisits = header['NVISITS']

	print('------------Target ' + str(i + 1) + '/' + str(targetCount) + ' ------------')
	positions = []
	for visit in range(1, nvisits + 1):
		data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
		if (nvisits != 1):
			ccf = data['CCF'][0][1+visit]
		else:
			ccf = data['CCF'][0]
		pos = getMaxPositions(ccf, 0.15)
		if (str(pos[0]) != 'none') and ((str(pos[1]) != 'none')):
			interestingTargets.append([locationID, apogeeID])
		positions.append(pos)
	
	reportPositions(locationID, apogeeID, positions)
reportTargets(interestingTargets, 'interestingTargets')
reportTargets(skippedTargets, 'skippedTargets')
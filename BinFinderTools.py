import numpy as np
import matplotlib.pyplot as plt
import apogee.tools.read as apread
import os

folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder2/'

def getAllTargets():
	data = apread.allStar(dr='13')
	return data['APOGEE_ID'], data['LOCATION_ID']

def calcR(x, pos1=0, pos2=401, peakLoc=201):
	'''
	Calculates the value of R with the given array x
	:return:  The value of R
	'''
	# if peakLoc is near the edges just skip it
	if (peakLoc <= 10) or (peakLoc >= 390):
		return np.nan
	tempMirror = (x[peakLoc:pos2])[::-1]
	sigmaA = np.sqrt(1.0 / (2.0 * len(tempMirror)) * np.sum((x[pos1:peakLoc] - tempMirror)**2))
	return np.max(x) / (np.sqrt(2.0) * sigmaA)

def findInflection(x):
	'''
	Finds the inflection points of the given curve if available.

	:param x:  The curve to find the inflection points of.
	:return: The position of the inflection points (left, right)
	'''
	maxPos = np.argmax(x)
	pos1, pos2 = -1, -1
	for i in range(maxPos, len(x) - 1):
		if (x[i + 1] - x[i] > 0):
			pos1 = i
			break
	for i in range(maxPos, 1, -1):
		if (x[i - 1] - x[i] > 0):
			pos2 = i
			break
	return pos2, pos1

def getMaxPositions(x, yBufferRange):
	'''
	Gets the positions of both maximums (if two exists) in the given array

	:param x: The array to find both maximums
	:param yBufferRange:  The minimum difference needed between the two maximums
	:return:  The position of both maximums (max1, max2)
	'''
	temp = np.array(x)
	max1 = np.nanargmax(x)
	pos1, pos2 = findInflection(temp)
	temp[pos1:pos2] = np.nan
	temp[np.where(temp < 0.2)] = np.nan

	# If we can find one, record the second maximum
	try:
		max2 = np.nanargmax(temp)
		'''
		# Check to see which inflection point is closest to peak 2
		if (np.abs(x[max1] - x[max2]) < yBufferRange):
			max2 = np.nan
		'''
		if (np.abs(max2 - pos1) < np.abs(max2 - pos2)):
			# Check if it's within the yBufferRange
			if (np.abs(x[max2] - x[pos1]) < yBufferRange):
				max2 = np.nan
		elif (np.abs(max2 - pos1) > np.abs(max2 - pos2)):
			if (np.abs(x[max2] - x[pos2]) < yBufferRange):
				max2 = np.nan
	except ValueError:
		max2 = np.nan
	
	# Double check that we are returning different positions
	if str(max1) == str(max2):
		max2 = np.nan
	
	return max1, max2

def recordTargets(targets, filename):
	targetCount = len(targets)

	if not os.path.exists(folder):
		os.makedirs(folder)
	filename = folder + filename + '.csv'
	f = open(filename, 'w')

	for i in range(targetCount):
		f.write("{0},{1},{2},{3}\n".format(targets[i][0], targets[i][1], targets[i][2]))
	f.close()

def reportPositions(locationID, apogeeID, ranger, positions):
	'''
	Records the positions of the maximums for each visit

	:param locationID:  The field ID of the target
	:param apogeeID: The apogee ID of the target
	:param ranger: The range used for yBufferRange in getMaxPositions
	:param positions: The positions of the (potentially two) maximums
	'''
	if positions == []:
		return
	
	visitCount = len(positions)

	if not os.path.exists(folder + str(round(ranger, 2)) + '/' + str(locationID) + '/'):
		os.makedirs(folder + str(round(ranger, 2)) + '/' + str(locationID) + '/')
	filename = folder + str(round(ranger, 2)) + '/' + str(locationID) + '/' + str(apogeeID) + '.tbl'
	f = open(filename, 'w')

	
	f.write('visit\tmax1\tmax2\trpeak\t')
	for i in range(len(positions[0][2])):
		f.write('r'+str(i+1)+'\t\t\t')
	f.write('\n')

	for i in range(visitCount):
		f.write(str(i + 1))
		position = positions[i]
		# probably a more elegantly way. just doing some quick codin
		# record postions of maximums
		f.write(',' + str(position[0]))
		f.write(',' + str(position[1]))
		# record r values
		for val in position[2]:
			f.write(',' + str(val))
		f.write('\n')
	f.close()

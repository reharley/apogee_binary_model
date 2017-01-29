import numpy as np
import matplotlib.pyplot as plt
import os
from BFData import BFData

hi = BFData('4424', '2M00000032+5737103', 0.02)
print(hi.apogeeID)
print(hi.locationID)
print(hi.ranger)
print(hi.filename)

for visit in range(len(hi.max1)):
	print('max1', visit + 1, hi.max1[visit])

for visit in range(len(hi.max2)):
	print('max2', visit + 1, hi.max2[visit])
	
for visit in range(len(hi.r)):
	print('r', visit + 1, hi.r[visit])
'''for r in hi.r:
	print(r)'''


folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder/'

def calcR(x, pos1=0, pos2=401):
	'''
	Calculates the value of R with the given array x
	:return:  The value of R
	'''	
	ccfCenter = 201
	pos1+= 1
	tempMirror = (x[ccfCenter:pos2])[::-1]
	sigmaA = np.sqrt(1.0 / (2.0 * len(tempMirror)) * np.sum((x[pos1:ccfCenter] - tempMirror)**2))
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
			max2 = 'none'
		'''
		if (np.abs(max2 - pos1) < np.abs(max2 - pos2)):
			# Check if it's within the yBufferRange
			if (np.abs(x[max2] - x[pos1]) < yBufferRange):
				max2 = 'none'
		elif (np.abs(max2 - pos1) > np.abs(max2 - pos2)):
			if (np.abs(x[max2] - x[pos2]) < yBufferRange):
				max2 = 'none'
	except ValueError:
		max2 = 'none'
	
	# Double check that we are returning different positions
	if str(max1) == str(max2):
		max2 = 'none'
	
	return max1, max2

def recordTargets(targets, ranger, filename):
	targetCount = len(targets)

	if not os.path.exists(folder + str(round(ranger, 2)) + '/'):
		os.makedirs(folder + str(round(ranger, 2)) + '/')
	filename = folder + str(round(ranger, 2)) + '/' + filename + '.csv'
	f = open(filename, 'w')

	for i in range(targetCount):
		f.write(str(targets[i][0]) + ',' + str(targets[i][1]) + '\n')
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

	
	f.write('visit\tmax1\tmax2\t')
	for i in range(len(positions[0][2])):
		f.write('r'+str(i+1)+'\t\t\t')
	f.write('\n')

	for i in range(visitCount):
		f.write(str(i + 1))
		position = positions[i]
		# probably a more elegantly way. just doing some quick codin
		# record postions of maximums
		f.write('\t\t' + str(position[0]))
		f.write('\t\t' + str(position[1]))
		# record r values
		for val in position[2]:
			f.write('\t' + str(val))
		f.write('\n')
	f.close()


import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from multiprocessing import Process
from Queue import Queue

folder = '/Volumes/CoveyData/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder/'

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


def reportPositions(locationID, apogeeID, ranger, positions):
	'''
	Records the positions of the maximums for each visit

	:param locationID:  The field ID of the target
	:param apogeeID: The apogee ID of the target
	:param ranger: The range used for yBufferRange in getMaxPositions
	:param positions: The positions of the (potentially two) maximums
	'''
	visitCount = len(positions)

	if not os.path.exists(folder + str(round(ranger, 2)) + '/' + str(locationID) + '/'):
		os.makedirs(folder + str(round(ranger, 2)) + '/' + str(locationID) + '/')
	filename = folder + str(round(ranger, 2)) + '/' + str(locationID) + '/' + str(apogeeID) + '.tbl'
	f = open(filename, 'w')

	f.write('visit\tmax1\tmax2\tR\n')
	for i in range(visitCount):
		f.write(str(i + 1))
		for val in positions[i]:
			f.write('\t\t' + str(val))
		f.write('\n')
	f.close()

def calcR(x, pos1=101, pos2=None):
	'''
	Calculates the value of R with the given array x
	:param x: The array to calculate the R for
	:return:  The value of R
	'''
	maxPos = np.argmax(x)
	maxVal = x[maxPos]
	ccfCenter = 201

	# Check if we are doing a general r calculation or we have 2 distinct peaks
	if pos2 is None:
		tempMirror = (x[ccfCenter:301])[::-1]
	else:
		# Make sure that the bounds are symmetric
		if (np.abs(pos2 - ccfCenter) <= np.abs(pos1 - ccfCenter)):
			pos1-= 50
			pos2 = ccfCenter + (np.abs(pos1 - ccfCenter))
		else:
			pos2+= 50
			pos1 = ccfCenter - (np.abs(pos2 - ccfCenter))
		tempMirror = (x[ccfCenter:pos2])[::-1]

	sigmaA = np.sqrt( 1.0 / (2 * len(tempMirror)) * np.sum((x[pos1:ccfCenter] - tempMirror)**2))
	return maxVal / ( np.sqrt(2) * sigmaA)

def reportTargets(targets, ranger, filename):
	'''
	Recrods the targets of interes/skipped

	:param targets: The list of targets format: [(locationID, apogeeID), ...]
	:param ranger:  The range used in yBufferTange in getMaxPositions
	:param filename:  The name of the file to use
	'''
	targetCount = len(targets)

	if not os.path.exists(folder + str(round(ranger, 2)) + '/'):
		os.makedirs(folder + str(round(ranger, 2)) + '/')
	filename = folder + str(round(ranger, 2)) + '/' + filename + '.csv'
	f = open(filename, 'w')

	for i in range(targetCount):
		f.write(str(targets[i][0]) + ',' + str(targets[i][1]) + '\n')
	f.close()

def runFinder(ranger):
	interestingTargets = []
	skippedTargets = []
	locationID = 4590
	apogeeID = '2M00050265+0116236'
	interestingTarget = False

	badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
	skippedTargets.append([locationID, apogeeID])

	nvisits = header['NVISITS']
	'''sys.stdout.write("\r{0}\t\t\t".format('Target ' + str(i + 1) + '/' + str(targetCount)))
	sys.stdout.flush()'''
	positions = []
	for visit in range(1, nvisits + 1):
		data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
		if (nvisits != 1):
			ccf = data['CCF'][0][1 + visit]
		else:
			ccf = data['CCF'][0]

		pos = getMaxPositions(ccf, ranger)
		r = calcR(ccf)
		if (str(pos[0]) != 'none') and ((str(pos[1]) != 'none')):
			interestingTarget = True
			# r = calcR(ccf, pos[0], pos[1])
		'''elif r < 1.0:
			interestingTarget = True'''

		positions.append([pos[0], pos[1], r])

	# reportPositions(locationID, apogeeID, ranger, positions)
	if interestingTarget == True:
		interestingTargets.append([locationID, apogeeID])
		interestingTarget = False

	reportTargets(interestingTargets, ranger, 'interestingTargets')
	reportTargets(skippedTargets, ranger, 'skippedTargets')
	del interestingTargets[:]
	del skippedTargets[:]

print('\n------------Range ' + str(0.25) + '------------\n')
runFinder(0.25)

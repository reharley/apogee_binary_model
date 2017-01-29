# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import matplotlib.pyplot as plt
import apogee.tools.read as apread

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

	sigmaA = np.sqrt( 1.0 / (2.0 * len(tempMirror)) * np.sum((x[pos1:ccfCenter] - tempMirror)**2))
	return maxVal / ( np.sqrt(2.0) * sigmaA)


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
			print('ballo')
			print(np.abs(x[max2] - x[pos1]))
			# Check if it's within the yBufferRange
			if (np.abs(x[max2] - x[pos1]) < yBufferRange):
				max2 = 'none'
		elif (np.abs(max2 - pos1) > np.abs(max2 - pos2)):
			print('hollo')
			print(np.abs(x[max2] - x[pos2]))
			if (np.abs(x[max2] - x[pos2]) < yBufferRange):
				max2 = 'none'
	except ValueError:
		print('hello')
		max2 = 'none'
	
	# Double check that we are returning different positions
	if str(max1) == str(max2):
		print('yolo')
		max2 = 'none'
	
	return max1, max2

locationID = 4602
apogeeID = '2M06502133+2755152'
print(locationID, apogeeID)
badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')

nvisits = header['NVISITS']
for visit in range(1, nvisits + 1):
	if (nvisits != 1):
		ccf = data['CCF'][0][1 + visit]
	else:
		ccf = data['CCF'][0]
	
	max1, max2 = getMaxPositions(ccf, 0.15)
	print(max2)
	print(calcR(ccf))
	if str(max1) != 'none':
		plt.scatter(max1, ccf[max1], color='red', s=30)
	if str(max2) != 'none':
		plt.scatter(max2, ccf[max2], color='orange', s=70)
	plt.plot(ccf, color='blue')
	plt.show()
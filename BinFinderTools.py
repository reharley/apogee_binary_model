import numpy as np
import apogee.tools.read as apread
import os
from BFData import BFData
import matplotlib.pyplot as plt

folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/'

def getAllTargets():
	'''
	Returns all targets from the allStar file
	:return: locationIDs, apogeeIDs
	'''
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

def getMaxPositions(x):
	'''
	Gets the positions of both maximums (if two exists) in the given array

	:param x: The array to find both maximums
	:return:  The position of both maximums and the peak height difference (max1, max2, peakhDiff)
	'''
	temp = np.array(x)
	max1 = np.nanargmax(x)
	peakhDiff = np.nan
	pos1, pos2 = findInflection(temp)
	temp[pos1:pos2] = np.nan
	temp[np.where(temp < 0.2)] = np.nan

	# If we can find one, record the second maximum
	try:
		max2 = np.nanargmax(temp)
		peakhDiff = abs(x[max1] - x[max2])
		'''
		# Check to see which inflection point is closest to peak 2
		if (np.abs(x[max1] - x[max2]) < yBufferRange):
			max2 = np.nan
		'''
		'''if (np.abs(max2 - pos1) < np.abs(max2 - pos2)):
			# Check if it's within the yBufferRange
			if (np.abs(x[max2] - x[pos1]) < yBufferRange):
				max2 = np.nan
		elif (np.abs(max2 - pos1) > np.abs(max2 - pos2)):
			if (np.abs(x[max2] - x[pos2]) < yBufferRange):
				max2 = np.nan'''
	except ValueError:
		max2 = np.nan
		peakhDiff = np.nan
	
	# Double check that we are returning different positions
	if str(max1) == str(max2):
		peakhDiff = np.nan
		max2 = np.nan
	
	return max1, max2, peakhDiff

def recordTargetsCSV(targets, filename):
	'''
	Records the targets given into a csv file with the name filename

	:param targets: The targets ex: [locationIDs, apogeeIDs]
	:param filename: Name of the file
	'''
	targetCount = len(targets)

	if not os.path.exists(folder):
		os.makedirs(folder)
	filename = folder + filename + '.csv'
	f = open(filename, 'w')

	for i in range(targetCount):
		f.write("{0},{1}\n".format(targets[i][0], targets[i][1]))
	f.close()

def recordBFData(locationID, apogeeID, positions):
	'''
	Records all the data BinaryFinder finds

	:param locationID: The field ID of the target
	:param apogeeID: The apogee ID of the target
	:param positions: The positions of the (potentially two) maximums
	'''
	if positions == []:
		return
	
	visitCount = len(positions)

	if not os.path.exists(folder + str(locationID) + '/'):
		os.makedirs(folder + str(locationID) + '/')
	filename = folder + str(locationID) + '/' + str(apogeeID) + '.csv'
	f = open(filename, 'w')

	
	f.write('visit,snr,max1,max2,peakhDiff,rpeak')
	for i in range(len(positions[0][4])):
		f.write(',r'+str(i+1))
	f.write('\n')

	for i in range(visitCount):
		f.write(str(i + 1))
		position = positions[i]
		# probably a more elegantly way. just doing some quick codin
		# record postions of maximums
		f.write(',' + str(position[0]))
		f.write(',' + str(position[1]))
		f.write(',' + str(position[2]))
		f.write(',' + str(position[3]))
		# record r values
		for val in position[4]:
			f.write(',' + str(val))
		f.write('\n')
	f.close()

def recordTargets(locationIDs, apogeeIDs):
	'''
	With the given field and 2M IDs, record all the BFData
	:param locationIDs: Field IDs
	:param apogeeIDs: 2M IDs
	'''
	interestingTargetsr = []
	interestingTargetsDualPeak = []
	skippedTargets = []
	
	targetCount = len(locationIDs)
	for i in range(targetCount):
		locationID = locationIDs[i]
		apogeeID = apogeeIDs[i]

		# Get fits files
		try:
			badheader, header = apread.apStar(locationID, apogeeID, ext=0, dr='13', header=True)
			data = apread.apStar(locationID, apogeeID, ext=9, header=False, dr='13')
		except IOError:
			skippedTargets.append([locationID, apogeeID])
			continue
		
		# Calculate r and test for second peak
		nvisits = header['NVISITS']

		positions = []
		rRecorded = False
		dpRecorded = False
		for visit in range(0, nvisits):
			if (nvisits != 1):
				ccf = data['CCF'][0][2 + visit]
				snr = header['SNRVIS' + str(1+visit)]
			else:
				ccf = data['CCF'][0]
				snr = header['SNRVIS1']
			max1, max2, peakhDiff = getMaxPositions(ccf)
			
			# Calculate r values
			r = []

			# Calculate r by reflecting about the highest peak
			ccfCount = len(ccf)
			if max2 != np.nan:
				peakLoc = max(max1, max2)
			else:
				peakLoc = max1

			try:
				if (ccfCount > peakLoc*2):
					r.append(calcR(ccf, pos2=peakLoc*2, peakLoc=peakLoc))
				else:
					r.append(calcR(ccf, pos1=2*peakLoc-ccfCount+1, pos2=ccfCount-1, peakLoc=peakLoc))
			except:
				r.append(np.nan)
				print(locationID, apogeeID)
			
			# calculate r by reflecting about the center (201)
			for cut in range(20):
				r.append(calcR(ccf, pos1=cut*10+1, pos2=(401 - (cut * 10)), peakLoc=201))
			
			if (r[0] < 7.0) and (rRecorded is False):
				rRecorded = True
				interestingTargetsr.append([locationID, apogeeID])

			if (np.isnan(max2) == False) and (dpRecorded is False):
				dpRecorded = True
				interestingTargetsDualPeak.append([locationID, apogeeID])

			positions.append([snr, max1, max2, peakhDiff, r])
		
		recordBFData(locationID, apogeeID, positions)

	recordTargetsCSV(interestingTargetsr, 'interestingTargetsr')
	recordTargetsCSV(interestingTargetsDualPeak, 'interestingTargetsDualPeak')
	recordTargetsCSV(skippedTargets, 'skippedTargets')

def genPeakHCutTable(locationIDs, apogeeIDs, filename):
	'''
	Generate peakhTable
	:param locationIDs: Field ID
	:param apogeeIDs: 2M ID
	:param filename: file
	'''
	targetCount = len(locationIDs)
	data = []
	for i in range(targetCount):
		locationID = locationIDs[i]
		apogeeID = apogeeIDs[i]

		if (BFData.exists(locationID, apogeeID)):
			data.append(BFData(locationID, apogeeID))
	
	thoseRs = []
	for i in range(11, 15):
		thoseRs.append(np.array([x.lowestR(i) for x in data]))
	
	thoseRPeaks = np.array([x.lowestRPeak() for x in data])
	'''thosehDiffs = np.array([x.longestHDiff() for x in data])
	print(thosehDiffs)
	print(np.argwhere(thosehDiffs < 0.2))
	indices = np.argwhere(thosehDiffs < 0.01)
	recordTargetsCSV([locationIDs[indices], apogeeIDs[indices]], 'raptors')'''
	filename = folder + filename + '.csv'
	if not os.path.exists(folder):
		os.makedirs(folder)
	f = open(filename, 'w')
	
	f.write('R_Th')
	for i in range(len(thoseRs)):
		f.write(',R_Th>R{0},pop%'.format(i+11))
	f.write(',R_Th>RP,pop%\n')

	rCounts = [ [], [], [], [] ]
	rPeakCounts = []
	x = []
	for i in range(80):
		x.append(i*0.5)
		f.write(str(i*0.5))
		for j in range(len(thoseRs)):
			rCount = len(np.where(i*0.5 > thoseRs[j])[0])
			rCounts[j].append(rCount/float(targetCount))
			f.write(',{0},{1}%'.format(rCount, round(rCount/float(targetCount)*100., 2)))
		
		rPeakCount = len(np.where(i*0.5 > thoseRPeaks)[0])
		rPeakCounts.append(rPeakCount/float(targetCount))
		f.write(',{0},{1}%\n'.format(rPeakCount, round(rPeakCount/float(targetCount)*100., 2)))
	f.close()

	plt.title('Number Of Targets Where R_Th > R_Target')
	for i in range(len(rCounts)):
		plt.plot(x, rCounts[i], label='r{0} pop%'.format(11+i))
	plt.plot(x, rPeakCounts, label='rpeak pop%')
	plt.xlabel('R')
	plt.ylabel('Population %')
	plt.legend()
	plt.show()

def removeSingle(locationIDs, apogeeIDs, filename):
	'''
	Removes all single targets from the lists provided
	:param locationIDs: Field IDs
	:param apogeeIDs: 2M IDs
	:param filename: filename
	:return: [locationIDs, apogeeIDs]
	'''
	targetCount = len(locationIDs)

	data = []
	for j in range(targetCount):
		locationID = locationIDs[j]
		apogeeID = apogeeIDs[j]

		if (BFData.exists(locationID, apogeeID)):
			data.append(BFData(locationID, apogeeID))
	print('here')

	max2s = np.array([x.max2 for x in data])

	count = len(max2s)
	singleTargets = []
	indices = []
	for i in range(count):
		if (np.all(np.isnan(max2s[i]))):
			singleTargets.append([locationIDs[i], apogeeIDs[i]])
			indices.append(i)
	
	recordTargetsCSV(singleTargets, '{0}_single'.format(filename))
	
	return np.delete(locationIDs, indices), np.delete(apogeeIDs, indices)

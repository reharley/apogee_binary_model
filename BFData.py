import numpy as np
import os

class BFData:
	def __init__(self, locationID, apogeeID):
		'''
		Initializes the BFData object.
		You can check whether or not the data for the object exists using BFData.exists(locationID, apogeeID)
		:param locationID: Field ID of the BFData object
		:param apogeeID: The 2M ID
		'''
		folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/'
		self.apogeeID = apogeeID
		self.locationID = locationID
		self.filename = folder + str(locationID) + '/' + str(apogeeID) + '.csv'
		self.max1 = []
		self.max2 = []
		self.r = []
		self.peakhDiff = []
		self.rPeak = []
		self.snr = []

		data = np.loadtxt(self.filename, delimiter=',', dtype=str,skiprows=1)
		if len(data.shape) == 1:
			self.snr.append(data[1].astype(float))
			self.max1.append(data[2].astype(float))
			self.max2.append(data[3].astype(float))
			self.peakhDiff.append(data[4].astype(float))
			self.rPeak.append(data[5].astype(float))
			self.r.append(data[6:].astype(float))
		else:
			for visit in data:
				self.snr.append(visit[1].astype(float))
				self.max1.append(visit[2].astype(float))
				self.max2.append(visit[3].astype(float))
				self.peakhDiff.append(visit[4].astype(float))
				self.rPeak.append(visit[5].astype(float))
				self.r.append(visit[6:].astype(float))

	def lowestR(self, window):
		'''
		Returns the lowest r value of all the visits in the given window slice.
		The r values here are all calculated with the center of the ccf (201) being the reflection point.
		:param window: The window to find r at
		:return: The lowest r value
		'''
		count = len(self.r)

		if (count == 1):
			return self.r[0][window]
		else:
			temp = self.r[0][window]
			for i in range(count):
				if(temp > self.r[i][window]):
					temp = self.r[i][window]
			return temp

	def lowestRPeak(self):
		'''
		Returns the lowest r value of all the visits.
		The rpeak values are calculated with the peak being the reflection point.
		:return: The lowest r value
		'''
		count = len(self.rPeak)

		if (count == 1):
			return self.rPeak[0]
		else:
			temp = self.rPeak[0]
			for i in range(count):
				if(temp > self.rPeak[i]):
					temp = self.rPeak[i]
			return temp
	
	def peakSeperation(self):
		'''
		Gets the horizontal seperation between the peaks
		:return: Seperation in ccf lag units
		'''
		return np.abs(np.array(self.max2) - np.array(self.max1))

	def longestHDiff(self):
		'''

		:return:
		'''
		count = len(self.peakhDiff)
		if np.isnan(self.max2) is True:
			return np.nan

		if (count == 1):
			return self.peakhDiff[0]
		else:
			temp = self.peakhDiff[0]
			for i in range(count):
				if(temp < self.peakhDiff[i]):
					temp = self.peakhDiff[i]
			return temp
	
	def deltaR(self, initWindow=12, finalWindow=15):
		'''
		Gets the average change in r within a given window for all visits

		:param initWindow: The initial window
		:param finalWindow: The final window
		:return: The avg change in r for all visits
		'''
		# window slices we are using to get the avg change in 
		count = len(self.r)
		deltaRs = []
		if (count == 1):
			return deltaRs.append(self.r[0][finalWindow] - self.r[0][initWindow])
		else:
			for i in range(count):
				deltaRs.append(self.r[i][finalWindow] - self.r[i][initWindow])
		return deltaRs

	def secondPeak(self):
		'''
		Checks to see whether or not the target has a second peak
		:return: True if there is a second peak, false otherwise.
		'''
		count = len(self.max2)

		if (count == 1):
			return not np.isnan(self.max2[0])
		else:
			for i in range(count):
				if(np.isnan(self.max2[i]) is False):
					return True
		return False

	@staticmethod
	def exists(locationID, apogeeID):
		'''
		Checks whether or notBinaryFinder was able to aquiret the data on the target.
		TODO: aquire the data if it doesn't exist??

		:param locationID: Field ID of the target
		:param apogeeID: 2M ID of the target
		:return: True if the data exists, false otherwise
		'''
		folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/'
		filename = '{0}{1}/{2}.csv'.format(folder, locationID, apogeeID)
		if not os.path.exists(filename):
			return False
		return True
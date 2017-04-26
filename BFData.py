import numpy as np
import os

class BFData:
	def __init__(self, locationID, apogeeID):
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

	def lowestR(self, slice):
		count = len(self.r)

		if (count == 1):
			return self.r[0][slice]
		else:
			temp = self.r[0][slice]
			for i in range(count):
				if(temp > self.r[i][slice]):
					temp = self.r[i][slice]
			return temp

	def lowestRPeak(self):
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
		return np.abs(np.array(self.max2) - np.array(self.max1))

	def longestHDiff(self):
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
		count = len(self.max2)

		if (count == 1):
			print(not np.isnan(self.max2[0]), self.max2[0])
			return not np.isnan(self.max2[0])
		else:
			for i in range(count):
				print(np.isnan(self.max2[i]), self.max2[i])
				if(np.isnan(self.max2[i]) is False):
					return True
		return False

	@staticmethod
	def exists(locationID, apogeeID):
		folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/'
		filename = '{0}{1}/{2}.csv'.format(folder, locationID, apogeeID)
		if not os.path.exists(filename):
			return False
		return True
import numpy as np

class BFData:
	def __init__(self, locationID='', apogeeID='',ranger=''):
		folder = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder2/'
		
		self.apogeeID = apogeeID
		self.locationID = locationID
		self.ranger = ranger
		self.filename = folder + str(ranger) + '/' + str(locationID) + '/' + str(apogeeID) + '.tbl'
		self.max1 = []
		self.max2 = []
		self.r = []
		self.rPeak = []
		
		data = np.loadtxt(self.filename, delimiter='\t', dtype=str,skiprows=1)
		print(data)
		for visit in data:
			self.max1.append(visit[1])
			self.max2.append(visit[2])
			self.rPeak.append(visit[3])
			self.r.append(visit[4:].astype(float))
	
	def lowestR(self, slice):
		count = len(self.r)

		if (count == 1):
			return self.r[slice]
		else:
			temp = self.r[0][slice]
			for i in range(count):
				if(temp > self.r[i][slice]):
					temp = self.r[i][slice]
			return temp
		
		#just in case
		return -1.0
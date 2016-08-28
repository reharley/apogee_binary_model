import apogee.tools.read as apread

from BinModelGen import getRVs
from ModelParams import ModelParams


class GridParam:
	'''
	Simple wrapper to make the grid easier to use.
	Stores the best fit params based on the grid.
	If a target has not been passed through the grid then it the default values will be used.
	'''
	maxTeffA = 7999.			# Default max range of the Teff of the secondary component varying
	minTeffA = 3500.			# Default min range of the Teff of the secondary component varying
	maxTeffB = 7999.			# Default max range of the Teff of the secondary component varying
	minTeffB = 3500.			# Default min range of the Teff of the secondary component varying
	minFluxRatio = 0.3		# Default min range of the flux ratio of the secondary component varying
	maxFluxRatio = 1.0		# Default max range of the flux ratio of the secondary component varying
	minRVA = -200.		# Default max range of the flux ratio of the secondary component varying
	minRVB = -200.		# Default max range of the flux ratio of the secondary component varying
	maxRVA = 200.		# Default max range of the flux ratio of the secondary component varying
	maxRVB = 200.		# Default max range of the flux ratio of the secondary component varying
	teffStepA = 50.
	teffStepB = 50.
	rvAStep = 20.
	rvBStep = 20.
	fluxStep = 0.1
	modelParamA = None # Contains the parameters for the model
	modelParamB = None # Contains the parameters for the model
	visit = 0
	chi2 = -1.0
	passes = 0
	def __init__(self, loc_ID, apog_ID):
		'''
		Constructor

		:param loc_ID: [in] Location ID to assign the object
		:param apog_ID: [in] Apogee ID to assign the object
		'''
		self.apogeeID = apog_ID
		self.locationID = loc_ID
		self.modelParamA = ModelParams()
		self.modelParamB = ModelParams()

	def constructParams(self):
		'''
		Constructs the parameter given the data table provided in HDU9 of the targets apStar file.
		'''
		data = apread.apStar(self.locationID, self.apogeeID, ext=9, header=False)
		self.modelParamA.constructParams(data)
		self.modelParamB.constructParams(data)
		self.maxTeffA = self.modelParamA.teff + 100.
		self.minTeffA = self.modelParamA.teff - 100.
		self.teffStepA = 50.
		self.maxTeffB = self.maxTeffA + 100.
		self.minTeffB = self.minTeffA - 100.
		self.teffStepB = self.teffStepA

	def getRVs(self, visit):
		'''
		Gets the relative vhelio for the primary and secondary component (could be swapped every now and then)
		:param visit: [in] The visit to get the rvs of
		'''
		rva, rvb = getRVs(self.locationID, self.apogeeID, visit)
		self.modelParamA.rv = rva
		self.modelParamB.rv = rvb
		self.minRVA = rva - 2.
		self.minRVB = rvb - 2.
		self.maxRVA = rva + 2.
		self.maxRVB = rvb + 2.
		self.rvAStep = 0.4
		self.rvBStep = 0.4

	def setParams(self, visit, teffA, teffB, fluxRatio, rvA, rvB, chi2):
		'''
		Sets the given values to GridParam object and adjusts the ranges and step size of the target.
		:param visit: [in] The visit with the minimized chi2 value
		:param teffA: [in] The primary components teff
		:param teffB: [in] The secondary components teff
		:param fluxRatio:  [in] The secondary components flux ratio
		:param rvA: [in] The primary components rv value
		:param rvB: [in] The secondary components rv value
		:param chi2: [in] The current lowest chi2 value for this target
		'''
		self.passes+= 1
		self.visit = visit
		self.modelParamA.teff = teffA
		self.modelParamB.teff = teffB
		self.modelParamB.fluxRatio = fluxRatio
		self.modelParamA.rv = rvA
		self.modelParamB.rv = rvB
		self.chi2 = chi2

		# Adjust parameter limits depending on chi2
		if (chi2 < 10.):
			self.maxTeffA = teffA + 10.
			self.minTeffA = teffA - 10.
			self.teffStepA = 5.
			self.maxTeffB = teffB + 10.
			self.minTeffB = teffB - 10.
			self.teffStepB = 5.
			self.maxFluxRatio = fluxRatio + 0.02
			self.minFluxRatio = fluxRatio - 0.02
			self.fluxStep = 0.01
			self.maxRVA = rvA + .4
			self.minRVA = rvA - .4
			self.rvAStep = 0.1
			self.maxRVB = rvB + .4
			self.minRVB = rvB - .4
			self.rvBStep = 0.1
		elif (chi2 < 25.):
			self.maxTeffA = teffA + 25.
			self.minTeffA = teffA - 25.
			self.teffStepA = 10.
			self.maxTeffB = teffB + 25.
			self.minTeffB = teffB - 25.
			self.teffStepB = 10.
			self.maxFluxRatio = fluxRatio + 0.02
			self.minFluxRatio = fluxRatio - 0.02
			self.fluxStep = 0.01
			self.maxRVA = rvA + 1.
			self.minRVA = rvA - 1.
			self.rvAStep = 0.3
			self.maxRVB = rvB + 1.
			self.minRVB = rvB - 1.
			self.rvBStep = 0.3
		elif (chi2 < 100.):
			self.maxTeffA = teffA + 50.
			self.minTeffA = teffA - 50.
			self.teffStepA = 25.
			self.maxTeffB = teffB + 50.
			self.minTeffB = teffB - 50.
			self.teffStepB = 25.
			self.maxFluxRatio = fluxRatio + 0.05
			self.minFluxRatio = fluxRatio - 0.05
			self.fluxStep = 0.01
			self.maxRVA = rvA + 2.
			self.minRVA = rvA - 2.
			self.rvAStep = 0.5
			self.maxRVB = rvB + 2.
			self.minRVB = rvB - 2.
			self.rvBStep = 0.5
		else:
			self.maxTeffA = teffA + 100.
			self.minTeffA = teffA - 100.
			self.teffStepA = 25.
			self.maxTeffB = teffB + 100.
			self.minTeffB = teffB - 100.
			self.teffStepB = 25.
			self.maxFluxRatio = fluxRatio + 0.1
			self.minFluxRatio = fluxRatio - 0.1
			self.fluxStep = 0.04
			self.maxRVA = rvA + 10.
			self.minRVA = rvA - 10.
			self.rvAStep = 4.0
			self.maxRVB = rvB + 10.
			self.minRVB = rvB - 10.
			self.rvBStep = 4.0

	def checkParams(self):
		'''
		Checks the parameters to make sure they are not out of bounds of the model.
		'''
		self.modelParamA.checkParams()
		self.modelParamB.checkParams()

	def toStringHeader(self):
		'''
		Constructs the string header to add to the chi2 file
		:return: The string header to the chi2.lis file
		'''
		return '{0}{1}\t\t\t\t{2}\t{3}\t{4}\t{5}\t{6}\t\t{7}\t\t{8}\t{9}\n'.format('Field ID', '2MID', 'visit', 'TeffA', 'TeffB', 'Flux Ratio', 'RVA', 'RVB', 'Passes', 'chi2')

	def toString(self):
		'''
		Constructs string to add to the chi2 file
		:return: The formatted string containing the gridParams data
		'''
		return '{0}\t{1}\t{2}\t\t{3}\t{4}\t{5}\t{6}\t\t{7}\t{8}\t\t{9}\n'.format(self.locationID, self.apogeeID, self.visit,
					round(self.modelParamA.teff, 2), round(self.modelParamB.teff, 2), round(self.modelParamB.fluxRatio, 2),
					round(self.modelParamA.rv, 2), round(self.modelParamB.rv, 2), self.passes, round(self.chi2))

class ModelParams:
	'''
	Class that contains the data needed to generate the model using FERRE
	'''
	teff = 0.0			# effective temperature
	logg = 0.0			# surface gravity
	metals = 0.0		# metal abundance
	alphafe = 0.0		# alpha element
	nfe = 0.0			# nitrogen relative abundance
	cfe = 0.0			# carbon relative abundance
	fluxRatio = 1.0		# Flux ratio (1:x)
	rv = 0.0			# VHELIO

	def adjustParams(self, teff, fluxRatio):
		'''
		Changes the relevant parameters of the effective temperatures and flux ratios
		:param teff: [in] The new effective temperature of star B
		:param fluxRatio: [in] The new flux ratio between the primary and secondary components (1:fluxRatio respectively)
		'''
		# params[0][0] = TeffA
		self.teff = teff
		self.fluxRatio = fluxRatio
		self.checkParams()


	def checkParams(self):
		'''
		Makes sure the parameters for the model are not out of range of the GK or F library
		'''
		if (self.teff >= 8000.):
			self.teff = 7999.
		if (self.teff <= 3500.):
			self.teff = 3500.
		if (self.logg >= 5.0):
			self.logg = 4.9

	def constructParams(self, data):
		'''
		Assigns the approximated model parameters of a target
		:param data: [in] The nineth HDU of the targets fits file
		'''
		self.teff = data['TEFF'][0]
		self.logg = data['LOGG'][0]
		self.metals = data['FEH'][0]
		self.alphafe = data['ALPHA'][0]
		self.nfe = 0.0
		self.cfe = data['CARBON'][0]
		self.fluxRatio = 1.0
# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np
import matplotlib.pyplot as plot
import os
import itertools
import apogee.spec.plot as splot
from apogee.modelspec import ferre

class ParamData:
	# Contructor
	def __init__(self, data, name):
		self.data = np.array(data)
		self.constant = False
		self.constantVal = 0
		self.name = name


def genPlot(path, teff, logg, metals, am, nm, cm):
	# Get the model
	mspec= ferre.interpolate(teff,logg,metals,am,nm,cm)

	# Plot the model
	splot.waveregions(mspec,
					labelID='[N/M]=' + str(nm) + ', [C/M]=' + str(cm),
					labelTeff=teff,
					labellogg=logg,
					labelmetals=metals,
					labelafe=am)

	# Format and save the file
	fig = plot.gcf()
	fig.set_size_inches(30.0, 15.0, forward=True)
	plot.draw()

	if not os.path.exists('model_plots/' + path):
		os.makedirs('model_plots/' + path)
	
	plot.savefig('model_plots/' + path + '/' +
					str(teff) + '_' + str(logg) + '_'
					+ str(metals) + '_' + str(am) + '_'
					+ str(nm) + '_' + str(cm) + '.png',
					format='png', dpi=300)
	plot.clf()
	plot.close('all');

# Goes through each of the next parameters
def nextParam(combos, path, j, n):
	# Check to see more than 1 parameter is variable.
	if (combos.shape[1] >= n):
		for i in range(params[combos[j][n - 1]].data.shape[0]):
			finalParams[params[combos[j][n - 1]].name] = params[combos[j][n - 1]].data[i]
			
			# Make sure we aren't adding the same name
			if params[combos[j][n - 1]].name not in path:
				path+= path + '/' + params[combos[j][n - 1]].name

			nextParam(combos, path, j, n + 1)
	else:
		genPlot(path, finalParams['Teff'], 
				finalParams['logg'], finalParams['metals'], 
				finalParams['am'], finalParams['nm'], finalParams['cm'])

# Contains the list of available models
params = np.array([
	ParamData(np.arange(3500.0, 6000.0, 250.0), 'Teff'),# Teff available models.
	ParamData(np.arange(0.0, 5.0, 0.5), 'logg'),        # logg available models.
	ParamData(np.arange(-2.5, 0.5, 0.5), 'metals'),     # [M/H] available models.
	ParamData(np.arange(-1.0, 1.0, 0.25), 'am'),        # [C/m] available models.
	ParamData(np.arange(-1.0, 1.0, 0.5), 'nm'),         # [N/M] available models.
	ParamData(np.arange(-1.0, 1.0, 0.25), 'cm')	        # [alpha/M] available models.
])

#set default params
def setDefParams():
	finalParams['Teff'] = 3500.0
	finalParams['logg'] = 0.0
	finalParams['metals'] = -2.5
	finalParams['am'] = -1.0
	finalParams['nm'] = -1.0
	finalParams['cm'] = -1.0

# Contains the parameters to be printed
finalParams = dict()

setDefParams()

# Gets all possible combinations with 1-5 parameters held constant
for i in range(params.shape[0] - 1):
	# Get possible combinations with i + 1 parameters being variable
	combos = np.array(list(itertools.combinations(range(params.shape[0]), i + 1)))

	print(combos)
	print(combos.shape[0], 'possibilities.')
	# Go through all possible combinations with shape[1] being the number of variable parameters
	for j in range(combos.shape[0]):
		setDefParams()
		print(params[combos[j][0]].data.size, params[combos[j][0]].name)
		nextParam(combos, params[combos[j][0]].name, j, 1)
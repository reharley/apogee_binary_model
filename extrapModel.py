# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import mspecGen as mg
import numpy as np
from scipy.stats import chisquare
from apogee.modelspec import ferre
import apogee.tools.read as apread

# Current constants
teff1 = 5000.
teff2 = 5250.
logg = 4.7
metals = am = nm = cm = 0.

# Star stuff
visit = 1

# Create parameter arrays
params = [	[teff1, teff2],
			[logg, logg],
			[metals, metals],
			[am, am],
			[nm, nm],
			[cm, cm] ]

# Temperature values for our grid
maxTeff = 5500. # was 7500. need to check for which library to pull from. possibly just check in ferre.interpolate
minTeff = 3500.
rangeTeff = [ maxTeff, (maxTeff - minTeff)/2. + minTeff, minTeff]

def binaryGridFit(locationID, apogeeID, params, visit, rangeTeff):
	'''
	Fits binary via grid. More to come soon. Me hungry.
	
	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param params: The paramters to test against the observed data.
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	:param visit: The visit to test against.
	:param rangeTeff: The range of teff
	:return: The best fit params
	'''
	peak = np.full((len(rangeTeff), len(rangeTeff)), -1.)

	# Navigate grid
	for i in range(len(rangeTeff)):
		for j in range(len(rangeTeff)):
			# Assign the range values to test in params
			params[0][0], params[0][1] = rangeTeff[i], rangeTeff[j]
			binModel, peak[i][j] = mg.binaryModelGen(locationID, apogeeID, params, visit)
	
	# Get the max peak value
	print(np.max(np.max(peak, axis=1), axis=0))
	return params

locationIDs, apogeeIDs = np.loadtxt('binaries.dat', unpack=True, delimiter=',', dtype=str)
for i in range(len(locationIDs)):
	print(locationIDs[i], apogeeIDs[i])
	binaryGridFit(int(locationIDs[i]), apogeeIDs[i], params, visit, rangeTeff)
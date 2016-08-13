'''
Binary Model Spectrum Generation

This script generates a model based on the paramaters given.
These parameters are the Teff, logg, metals, [A/M] [N/M], [C/M].
Currently it is accepting an 2D array of these values assuming each have
two values for each star in the binary. This may change to accept more
parameters for optimization. (To probably 6 of each).
'''

import BinPlot
import numpy as np
import scipy.constants as const
import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre

def getMassRatio(apogeeID):
	'''
	Returns the mass ratio between the two stars in the binary system.
	Not all targets will have a mass ratio. If no ratio is recorded then -1 is returned

	:param apogeeID: The 2M ID
	:return: The mass ratio between the two stars. returns -1 if ratio was not found
	'''
	apogeeIDs, q = np.loadtxt('lists/gamma_q.dat', delimiter=',', skiprows=1, usecols=[0, 3], dtype=str, unpack=True)
	for i in range(len(apogeeIDs)):
		if (apogeeIDs[i] == apogeeID):
			return float(q[i])
	
	return -1.0

def getRVs(locationID, apogeeID, visit):
	'''
	Returns the velocities of the binar components.

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:return: The velocities of the individual binary components in the system.
	'''
	# Contains the dir that holds martins data (deltaV's)
	martin_data = '/Volumes/CoveyData/APOGEE_Spectra/Martin/Data/Highly_Likely/rv_tables/'
	
	# Get the Julian Dates, velocity of components A and B (km/s), and residual velocities (km/s)
	# TODO: just get the line we want... no need to load the whole file. line = visit
	jDates, velA, velB, residual = np.loadtxt(martin_data + str(locationID) + '_' + apogeeID + '_rvs.tbl', skiprows=1, unpack=True)

	# Get the master HDU of the binary
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)

	
	row = -1
	# Check if there is only one visit
	if (header['NVISITS'] == 1):
		return [ velA - velB, velB - velA ]
	# Find the correct row from the rvs table
	else:
		try:
			for i in range(header['NVISITS']):
				if (int(header['JD' + str(visit)] * 10) == int(jDates[i] * 10)):
					row = i
		except IndexError:
			print('WARNING: rvs table for ' + str(locationID) + ', ' + apogeeID + ' may not have the same visit count.')
			pass
	
	if(row == -1):
		raise Exception('ERROR: visit not found. Check rvs tables and master HDU of ' + str(locationID) + '_' + apogeeID)

	return [ velA[row], velB[row] ]

def shiftFlux(spec, vel):
	'''
	Shifts flux provided.

	May want to allow user to pass restLambda in so we don't generate it again...
	:param spec: The spectrum to shift
	:param vel: The velocity to shift by
	:return: The shifted spectrum
	'''
	# Generate the wavelength grid
	restLambda = splot.apStarWavegrid()

	if (len(spec.shape) > 1):
		# Calculates wavelength grid for the second star with a doppler shift
		shiftLambda = [restLambda * (1. + v / (const.c / 1000.)) for v in vel]
		# The fluxes of both stars
		shiftedFlux = [np.interp(restLambda, shiftLambda[i], spec[i]) for i in range(len(shiftLambda))]
	else:
		# Calculates wavelength grid for the second star with a doppler shift
		shiftLambda = restLambda * (1. + vel / (const.c / 1000.))
		# The fluxes of both stars
		shiftedFlux = np.interp(restLambda, shiftLambda, spec)
	return shiftedFlux

def binaryModelGen(locationID, apogeeID, params, visit, plot=True):
	'''
	Interpolates the spectra of the individual stars in the binary using some initial parameters and their velocity
	difference.

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param params: The paramters to test against the observed data.
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	:param visit: The visit to test against.
	:returns: The binary model flux and the maximum value from the cross correlation function between the modeled
	totalFlux and the continuum-normalized spectrum. (totalFlux, max)
	'''
	# Generate models (flux1, flux2)
	mspecs = ferre.interpolate(params[0], params[1], params[2],
							  params[3], params[4], params[5])
	for mspec in mspecs:
		mspec[np.isnan(mspec)] = 0.
	
	# Calculate deltaV
	RVs = getRVs(locationID, apogeeID, visit)
	
	# Generate the wavelength grid
	restLambda = splot.apStarWavegrid()
	# Calculates wavelength grid for the second star with a doppler shift
	shiftLambda = [restLambda * (1. + rv / (const.c / 1000.)) for rv in RVs]
	
	# The fluxes of both stars
	shiftedFlux = np.array([np.interp(restLambda, shiftLambda[i], mspecs[i]) for i in range(len(shiftLambda))])

	# The combined flux of the stars in the modeled binary (params[7][1] defined as flux ratio)
	totalFlux = (shiftedFlux[0] + (shiftedFlux[1] * params[6][1])) / 2.0

	# Make the plots
	if (plot == True):
		BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, mspecs[0], 'blue', 'rest model specA' ],
						 [ restLambda, mspecs[1], 'green', 'rest model specB' ],
						 [ restLambda, shiftedFlux[0], 'orange', 'shift model specA' ],
						 [ restLambda, shiftedFlux[1], 'purple', 'shift model specB' ]],
						[params[0][0], params[0][1]], 'Binary Model Gen - Prelim. Proc.', folder='model_gen');

	return totalFlux
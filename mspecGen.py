'''
Binary Model Spectrum Generation

This script generates a model based on the paramaters given.
These parameters are the Teff, logg, metals, [A/M] [N/M], [C/M].
Currently it is accepting an 2D array of these values assuming each have
two values for each star in the binary. This may change to accept more
parameters for optimization. (To probably 6 of each).
'''

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
from apogee.modelspec import ferre
import numpy as np
import scipy.constants as const

# Current constants
teff1 = 5000.
teff2 = 5250.
logg = 4.7
metals = am = nm = cm = 0.

# Star stuff
locationID = 4611
apogeeID = '2M05350392-0529033'
visit = 1

# Contains the dir that holds martins data (deltaV's)
martin_data = 'martin_data/'

# Create parameter arrays
params = [	[teff1, teff2],
			[logg, logg],
			[metals, metals],
			[am, am],
			[nm, nm],
			[cm, cm] ]


def calcDeltaRV(locationID, apogeeID, visit):
	'''
	Calculates the delta V for the binaries based on the visit we are testing against.

	Currently calculates velocity differences of (primary - secondary) and (secondary - primary) to account for the
	possibility of the veocities being associated to the wrong stars. If we determine this is unnecessary in the
	future we'll remove this.

	.. todo:: just get the line we want... no need to load the whole file. line = visit

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:return: The deltaV of the binary. [velA - velB, velB - velA]
	'''
	# Get the Julian Dates, velocity of components A and B (km/s), and residual velocities (km/s)
	# TODO: just get the line we want... no need to load the whole file. line = visit
	jDates, velA, velB, residual = np.loadtxt(martin_data + apogeeID + '_rvs.tbl', skiprows=1, unpack=True)

	# Get the master HDU of the binary
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)

	# Find the correct row from the rvs table
	row = -1
	try:
		for i in range(header['NVISITS']):
			if (int(header['JD' + str(visit)] * 10) == int(jDates[i] * 10)):
				row = i
	except IndexError:
		print('WARNING: rvs table for ' + apogeeID + ' may not have the same visit count.')
		pass

	if(row == -1):
		raise Exception('ERROR: visit not found. Check rvs tables and master HDU of ' + apogeeID)

	return [ velA[row] - velB[row], velB[row] - velA[row] ]

def binaryModelGen(locationID, apogeeID, params, deltaV, visit):
	'''
	Interpolates the spectra of the individual stars in the binary using some initial parameters and their velocity
	difference.

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param params: The paramters to test against the observed data.
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	:param deltaV: The relative velocity differences between the stars.
	:param visit: The visit to test against.
	:returns: The binary model flux. Currently returns 2 for each set of paramaters (see calcDeltaRV for details).
	'''
	# Generate models (flux1, flux2)
	mspec = ferre.interpolate(params[0], params[1], params[2],
							  params[3], params[4], params[5])
	# Fix to let np.interp work.
	for i in range(mspec.shape[0]):
		mspec[i][np.isnan(mspec[i])] = 0.
	
	# Generate the wavelength grid
	restLambda = splot.apStarWavegrid()
	# Calculates wavelength grid for the second star with a doppler shift
	shiftLambda = [restLambda * (1. + v / (const.c / 1000.)) for v in deltaV]

	# The fluxes of both stars
	shiftedFlux = [np.interp(restLambda, sLambda, mspec[0]) for sLambda in shiftLambda]
	# The combined flux of the stars
	totalFlux = [(sFlux + mspec[1]) / 2. for sFlux in shiftedFlux]

	# Get the continuum-normalized spectrum to subtract from the models
	cspec = apread.aspcapStar(locationID, apogeeID, ext=1, header=False)

	# Create array to normalize the cross correlation function output [2, 1) + [1, 2]
	norm = np.append(	np.linspace(2, 1, num=(len(cspec)/2), endpoint=False),
						np.linspace(1, 2, num=(len(cspec)/2) + 1))
	# Get Normalized cross correlation function between continuum-normalized spectra and the model spectra
	velNorm = np.convolve(cspec, totalFlux[0], mode='same') / norm
	# Get the pixel shift we need to correct for
	pixelShift = len(cspec)/2 - velNorm.argmax(axis=0)

	# If there is a pixel shift, lets get the correction
	if(pixelShift != 0):
		# Get the master HDU of the binary
		badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)

		# Heliocentric velocity (km/s) of visit 1
		helioV = header['VHELIO' + str(visit)]
		alpha = header['CDELT1']
		
		# Plug in shift into martins equation
		shiftCorrection = (10.**(alpha * pixelShift) - 1.) + helioV
		print('Shift correction', shiftCorrection)
	else:
		print('Pixel shift is 0 so there is no need to correct')

	return totalFlux

deltaV = calcDeltaRV(locationID, apogeeID, visit)
binaryModelGen(locationID, apogeeID, params, deltaV, visit)
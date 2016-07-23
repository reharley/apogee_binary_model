'''
Binary Model Spectrum Generation

This script generates a model based on the paramaters given.
These parameters are the Teff, logg, metals, [A/M] [N/M], [C/M].
Currently it is accepting an 2D array of these values assuming each have
two values for each star in the binary. This may change to accept more
parameters for optimization. (To probably 6 of each).
'''

import binPlot
import numpy as np
import scipy.constants as const
import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre

# Contains the dir that holds martins data (deltaV's)
martin_data = '/Volumes/CoveyData/APOGEE_Spectra/Martin/Data/Highly_Likely/rv_tables/'

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

	return [ velA[row] - velB[row], velB[row] - velA[row] ]

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
	mspec = ferre.interpolate(params[0], params[1], params[2],
							  params[3], params[4], params[5])
	# Fix to let np.interp work.
	for i in range(mspec.shape[0]):
		mspec[i][np.isnan(mspec[i])] = 0.
	
	# Calculate deltaV
	deltaV = calcDeltaRV(locationID, apogeeID, visit)
	
	# Generate the wavelength grid
	restLambda = splot.apStarWavegrid()
	# Calculates wavelength grid for the second star with a doppler shift
	shiftLambda = [restLambda * (1. + v / (const.c / 1000.)) for v in deltaV]

	# The fluxes of both stars
	shiftedFlux = [np.interp(restLambda, sLambda, mspec[0]) for sLambda in shiftLambda]
	# The combined flux of the stars in the modeled binary
	totalFlux = [(sFlux + mspec[1]) / 2. for sFlux in shiftedFlux]
	
	# Get the continuum-normalized spectrum to subtract from the models
	cspec = apread.aspcapStar(locationID, apogeeID, ext=1, header=False)
	cspecerr = apread.aspcapStar(locationID, apogeeID, ext=2, header=False)

	# Create array to normalize the cross correlation function output [2, 1) + [1, 2]
	norm = np.append(np.linspace(2, 1, num=(len(cspec)/2), endpoint=False),
					np.linspace(1, 2, num=(len(cspec)/2) + 1))
	# Get Normalized cross correlation function between continuum-normalized spectra and the model spectra
	pixelCorrelation = [np.correlate(tFlux, cspec, mode='same') for tFlux in totalFlux]
	pixelNorm = [pixelCorr / norm for pixelCorr in pixelCorrelation]
	
	# Get the pixel shift we need to correct for
	pixelShift = [len(cspec)/2 - pNorm.argmax(axis=0) for pNorm in pixelNorm]

	# TODO: Must... be... cleaner... way...
	# Use velocity that is closest to the correct shift
	if(np.abs(pixelShift[0]) < np.abs(pixelShift[1])):
		pixelShift = pixelShift[0]
		totalFlux = totalFlux[0]
		shiftLambda = shiftLambda[0]
		shiftedFlux = shiftedFlux[0]
		deltaV = deltaV[0]
		pixelCorrelation = pixelCorrelation[0]
		pixelNorm = pixelNorm[0]
	else:
		pixelShift = pixelShift[1]
		totalFlux = totalFlux[1]
		shiftLambda = shiftLambda[1]
		shiftedFlux = shiftedFlux[1]
		deltaV = deltaV[1]
		pixelCorrelation = pixelCorrelation[1]
		pixelNorm = pixelNorm[1]

	
	# If there is a pixel shift, lets get the correction
	if(pixelShift != 0):
		# Get the master HDU of the binary
		badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)

		# Heliocentric velocity (km/s) of visit 1
		helioV = header['VHELIO' + str(visit)]
		alpha = header['CDELT1']
		
		print('Delta V initial', deltaV)
		# Plug in shift into martins equation and correct the deltaV
		velocityCorrection = (10.**(alpha * pixelShift) - 1.) + helioV
		deltaV+= velocityCorrection

		# Calculates wavelength grid for the second star with a doppler shift
		shiftLambda = restLambda * (1. + deltaV / (const.c / 1000.))

		# The fluxes of both stars
		shiftedFlux = np.interp(restLambda, shiftLambda, mspec[0])
		# The combined flux of the stars in the modeled binary
		totalFlux = (shiftedFlux + mspec[1]) / 2.

		print('Shift correction', velocityCorrection)
		print('Delta V', deltaV)

	# Make the plots
	if (plot == True):
		binPlot.plotCCF(locationID, apogeeID, visit, restLambda, pixelNorm, params, 'norm');
		binPlot.plotCCF(locationID, apogeeID, visit, restLambda, pixelCorrelation, params, '');
		binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, mspec[0], 'blue', 'rest model specA' ],
						 [ restLambda, mspec[1], 'green', 'rest model specB' ],
						 [ restLambda, cspec, 'orange', 'cont-norm spec' ],
						 [ restLambda, shiftedFlux, 'purple', 'shift model specA' ]],
						params[0], 'Delta V Shift');

	return totalFlux, np.max(pixelNorm, axis=0), np.sum( ((cspec - totalFlux)/cspecerr)**2. )
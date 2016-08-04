# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import binPlot
from gif_gen import gifGen
import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.constants as const
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre
from apogee.spec import continuum

def printParams(params):
	'''
	Temp print function
	:param params: full parameter set
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	'''
	print('Teff A: ' + str(params[0]))
	print('logg A: ' + str(params[1]))
	print('metals A: ' + str(params[2]))
	print('am A: ' + str(params[3]))
	print('nm A: ' + str(params[4]))
	print('cm A: ' + str(params[5]))

locationIDs, apogeeIDs = np.loadtxt('lists/binaries2.dat', unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
for i in range(len(locationIDs)):
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	nvisits = header['NVISITS']
	print('Plotting: ' + locationIDs[i] + ', ' + apogeeIDs[i] + ', nvisits: ' + str(nvisits))
	print(str(i + 1) + '/' + str(targetCount) + ' targets completed')
	for visit in range(1, nvisits):
		data = apread.apStar(locationID, apogeeID, ext=9, header=False)
		spec = apread.apStar(locationID, apogeeID, ext=1, header=False)
		ccf = data['CCF'][0]
		if (nvisits != 1):
			spec = apread.apStar(locationID, apogeeID, ext=1, header=False)[1+visit]
			ccf = data['CCF'][0][1+visit]
		
		params = [ 	[data['TEFF'][0], 5500., 3500.],	# effective temperature
					[data['LOGG'][0], data['LOGG'][0], data['LOGG'][0]],	# surface gravity
					[data['FEH'][0], data['FEH'][0], data['FEH'][0]],	# metal abundance
					[data['ALPHA'][0], data['ALPHA'][0], data['ALPHA'][0]],	# α element
					[0.0, 0.0,0.0],	# nitrogen relative abundance
					[data['CARBON'][0], data['CARBON'][0], data['CARBON'][0]]]	# carbon relative abundance
		if (params[0][0] < 3500.):
			params[0][0] = 3500.
		if (params[0][0] >= 6000.):
			params[0][0] = 5500.
		if (params[1][0] >= 5.0):
			params[1][0] = params[1][2] = params[1][1] = 4.9 
		
		# Generate models (flux1, flux2)
		mspecs = ferre.interpolate(params[0], params[1], params[2],
									params[3], params[4], params[5])
		for mspec in mspecs:
			mspec[np.where(np.isnan(mspec))] = 0.0
		
		# prep obs spec
		spec[np.where(np.isnan(spec))] = 0.0
		spec = spec / max(spec)

		# Generate the wavelength grid
		restLambda = splot.apStarWavegrid()
		ccfs = []
		for mspec in mspecs:
			pixelCorrelation = scipy.correlate(spec, mspec, mode="full")
			pixelCorrelation = pixelCorrelation / max(pixelCorrelation)

			#Generate an x axis
			xcorr = np.arange(pixelCorrelation.size)
			#Convert this into lag units, but still not really physical
			lags = xcorr - (spec.size - 1)
			lagrange = 800
			temp = np.where(np.logical_or(lags == -lagrange, lags == lagrange))[0]
			ycorr_diff = pixelCorrelation - scipy.ndimage.filters.gaussian_filter1d(pixelCorrelation, 100)
			lags = lags[temp[0]:temp[1]]
			ycorr_diff = ycorr_diff[temp[0]:temp[1]]
			# store ccf
			ccfs.append(ycorr_diff)

			# Get the pixel shift we need to correct for
			pixelShift = len(ycorr_diff)/2 - ycorr_diff.argmax(axis=0)
			velocityShift = 0
			
			# If there is a pixel shift, lets get the correction
			if(pixelShift != 0):
				# Get the master HDU of the binary
				badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
				# Heliocentric velocity (km/s) of visit 1
				helioV = header['VHELIO' + str(visit)]
				alpha = header['CDELT1']
				# Plug in shift into martins equation and correct the deltaV
				velocityShift = (10.**(alpha * pixelShift) - 1.) + helioV

		binPlot.plotCOMPCCF(locationID, apogeeID, visit, velocityShift, 
							[	[ccfs[0], 'green', 'approx Teff'],
								[ccfs[1], 'blue', 'Hot Teff'],
								[ccfs[2], 'orange', 'Cool Teff']],
							params, '',folder='comparison_CCF')
		binPlot.plotCOMPCCF(locationID, apogeeID, visit, 'N/A', [[ccf, 'blue', 'Off. CCF']], params, '',folder='comparison_CCF_OFF')
		'''binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
					[[ restLambda, mspec, 'blue', 'rest model specA' ],
						[ restLambda, cspec, 'orange', 'cont-norm spec' ]],
					params, 'Delta V Shift', folder='comparison_deltav');'''

gifGen('comparison_CCF/')
gifGen('comparison_CCF_OFF/')
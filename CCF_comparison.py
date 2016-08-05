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
		specerr = apread.apStar(locationID, apogeeID, ext=2, header=False)
		ccf = data['CCF'][0]
		if (nvisits != 1):
			spec = apread.apStar(locationID, apogeeID, ext=1, header=False)[1+visit]
			specerr = apread.apStar(locationID, apogeeID, ext=2, header=False)[1+visit]
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
		# for mspec in mspecs:
		# 	mspec[np.where(np.isnan(mspec))] = 0.0

		# prep obs spec
		'''aspec= np.reshape(spec,(1,len(spec)))
		aspecerr= np.reshape(specerr,(1,len(specerr)))
		cont= spec / continuum.fit(aspec,aspecerr,type='aspcap')[0]'''
		spec[np.where(np.isnan(spec))] = 0.0
		cont = spec / max(spec)
		# Generate the wavelength grid
		restLambda = splot.apStarWavegrid()
		
		ccfs = []
		velocityShift = 0

		for mspec in mspecs:
			# nan_vals = np.where(np.isnan(mspec))[0]
			nan_vals = np.where(spec == 0.0)[0]
			chip_ranges = [(nan_vals[i] + 1, nan_vals[i+1]) for i in range(len(nan_vals) - 1) if nan_vals[i+1]!=nan_vals[i]+1]
			mspec[np.where(np.isnan(mspec))[0]] = 0.0
			ycorr = np.array([])
			lagrange = 200
			chipSize = 0
			# ycorr = scipy.correlate(cont[chip_ranges[0][0] - 100:chip_ranges[2][1] + 100], mspec[chip_ranges[0][0] - 100:chip_ranges[2][1] + 100], mode="full")
			for chipRange in chip_ranges:
				if (chipSize < chipRange[1] - chipRange[0]):
					chipSize = chipRange[1] - chipRange[0]
				midPoint = chipRange[0] + (chipRange[1] - chipRange[0])/2

				chipCCF = scipy.correlate(cont[chipRange[0]:chipRange[1]], mspec[chipRange[0]:chipRange[1]], mode="full")
				
				if (ycorr.size == 0):
					ycorr = chipCCF
				else:
					diff = (chipCCF.size - ycorr.size) / 2
					if (diff > 0):
						ycorr = np.append(np.zeros(diff + 1), ycorr)
						ycorr = np.append(ycorr, np.zeros(diff))
						# chipCCF = chipCCF[diff:]
					elif (diff < 0):
						chipCCF = np.append(np.zeros(-diff), chipCCF)
						chipCCF = np.append(chipCCF, np.zeros(-diff))
						# ycorr = ycorr[-diff:]
				ycorr+= chipCCF
				
				
			ycorr/= len(chip_ranges)
			ycorr-= np.median(ycorr)
			#Generate an x axis
			xcorr = np.arange(ycorr.size)
			#Convert this into lag units, but still not really physical
			# lags = xcorr - (1401 - 1)
			lags = xcorr - (chip_ranges[0][1] - chip_ranges[0][0] - 1)
			temp = np.where(np.logical_or(lags == -lagrange, lags == lagrange))[0]
			ycorr_diff = ycorr - scipy.ndimage.filters.gaussian_filter1d(ycorr, 100)
			lags = lags[temp[0]:temp[1]]
			ycorr_diff = ycorr_diff[temp[0]:temp[1]]
			ccfs.append(ycorr_diff)

			# Get the pixel shift we need to correct for
			pixelShift = len(ycorr_diff)/2 - ycorr_diff.argmax(axis=0)
			velocityShift = 0
			
			# Heliocentric velocity (km/s) of visit 1
			helioV = header['VHELIO' + str(visit)]
			alpha = header['CDELT1']

			velocityShift = (10.**(alpha * pixelShift) - 1.) #+ helioV
		# Calculates wavelength grid for the second star with a doppler shift
		shiftLambda = restLambda * (1. + velocityShift / (const.c / 1000.))

		# The flux of the model
		shiftedFlux = np.interp(restLambda, shiftLambda, mspecs[0])

		binPlot.plotCOMPCCF(locationID, apogeeID, visit, velocityShift, 
							[	[ccfs[0], 'green', 'approx Teff'],
								[ccfs[1], 'blue', 'Hot Teff'],
								[ccfs[2], 'orange', 'Cool Teff']],
							params, '',folder='comparison_CCF')
		binPlot.plotCOMPCCF(locationID, apogeeID, visit, header['VRAD' + str(visit)], [[ccf, 'blue', 'Off. CCF']], params, '',folder='comparison_CCF_OFF')
		binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
							[	[ restLambda, mspecs[0], 'blue', 'rest model' ],
								[ restLambda, cont, 'orange', 'cont-norm v. spec' ],
								[ restLambda, shiftedFlux, 'green', 'shifted model' ]],
								[0.0,0.0], 'Delta V Shift', folder='comparison_deltav');

gifGen('comparison_CCF/')
gifGen('comparison_CCF_OFF/')
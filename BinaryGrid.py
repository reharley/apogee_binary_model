'''
Contains the grid and the helper functions that run the grid. Currently the grid only varies the temperature of the
secondary component of the binary and its flux. This will change later and I may forget to update this summary.

An example of how the grid can be used is in RunGrid.py

The final results of the Grid can be found in lists/chi2.lis

With the individual target results found in lists/chi2/fieldID/2M_ID.lis

And if plot=True, then the plots can be found in plots/function/fieldID/2M_ID.png
'''
import BinPlot
import BinModelGen as bm
import os
import numpy as np
import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre
from apogee.spec import continuum

def checkParams(params):
	'''
	Makes sure the parameters for the model are not out of range of the GK library

	TODO: Not sure if passing by value or not... so return may be redundant...
	:param params: parameters for the model
	:return: corrected paramters
	'''
	if (params[0][0] >= 6000.):
		params[0][0] = 5999.
	if (params[0][0] <= 3500.):
		params[0][0] = 3500.
	if (params[1][0] >= 5.0):
		params[1][0] = 4.9
	if (params[0][1] >= 6000.):
		params[0][1] = 5999.
	if (params[0][1] <= 3500.):
		params[0][1] = 3500.
	if (params[1][1] >= 5.0):
		params[1][1] = 4.9
	return params

def constructParams(data):
	'''
	Constructs the approximated model parameters of a target
	:param data: The nineth HDU of the targets fits file
	:return: The model parameters of the target
	'''
	return [[data['TEFF'][0], data['TEFF'][0]],		# effective temperature
			[data['LOGG'][0], data['LOGG'][0]],		# surface gravity
			[data['FEH'][0], data['FEH'][0]],		# metal abundance
			[data['ALPHA'][0], data['ALPHA'][0]],  	# alpha element
			[0.0, 0.0],           					# nitrogen relative abundance
			[data['CARBON'][0], data['CARBON'][0]],	# carbon relative abundance
			[ 1.0, 1.0]]						# Flux ratio (1:x)

def adjustParams(params, TeffB, fluxRatio):
	'''
	Changes the relevant parameters of the effective temperatures and flux ratios
	:param params: The parameters to change
	:param TeffA: The new effective temperature of star A (will be added back later)
	:param TeffB: The new effective temperature of star B
	:param fluxRatio: The new flux ratio between the primary and secondary components (1:fluxRatio respectively)
	:return: The adjusted parameters
	'''
	# params[0][0] = TeffA
	params[0][1] = TeffB
	params[6][1] = fluxRatio
	return params

def getMinIndicies(x):
	'''
	Takes in a 3D array and finds the indicies of its minimum
	:param x: The array to find the min for
	:return: The indicies as a tuple (ind1, ind2, ind3)
	'''
	index = np.argmin(x)
	inds = np.where(x == np.min(x))
	ind = [i[0] for i in inds]
	return ind

def targetGrid(locationID, apogeeID, minTeff, maxTeff, minFluxRatio=0.6, maxFluxRatio=1.0, gridRes=10, plot=True):
	'''
	The grid tests against ranging effective temperatures for both stars and the flux ratio of the secondary component.
	This is done by target.

	:param locationID: The field ID of the target
	:param apogeeID: The 2 mass ID of the target
	:param minTeff: The minimum temperature to test against
	:param maxTeff: The maximum temperature to test against
	:param minFluxRatio: The minimum fluxRatio to test against (default=0.6)
	:param maxFluxRatio: The maximum fluxRatio to test against (default=1.0)
	:param gridRes: The amount of temperatures to test against within the range (default=5)
	:param plot: If true makes plots to see intermediate steps
	:return: The params and the corresponding chi2 value (params, chi2)
	'''
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	specs = apread.apStar(locationID, apogeeID, ext=1, header=False)
	specerrs = apread.apStar(locationID, apogeeID, ext=2, header=False)
	data = apread.apStar(locationID, apogeeID, ext=9, header=False)
	nvisits = header['NVISITS']

	# Prepare grid ranges
	rangeTeff = np.linspace(minTeff, maxTeff, num=gridRes)
	rangeFluxRatio = np.linspace(minFluxRatio, maxFluxRatio, num=gridRes)
	chi2 = np.full((nvisits, len(rangeTeff), len(rangeFluxRatio)), -1.)
	# chi2 = np.full((nvisits, len(rangeTeff), len(rangeTeff), len(rangeFluxRatio)), -1.)

	# Create file to store all the chi2 values
	path = 'lists/chi2/' + str(locationID) + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	fn = open(path + apogeeID + '.lis', 'w')
	fn.write('{0}\t{1}\t\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format('Field ID', '2MID', 'visit', 'TeffA', 'TeffB', 'Flux Ratio', 'chi2'))
	for visit in range(1, nvisits + 1):
		if (nvisits != 1):
			spec = specs[1+visit]
			specerr = specerrs[1+visit]
		else:
			spec = specs
			specerr = specerrs
		# Temperature values for our grid
		maxTeff = 5999. # was 7500.
		minTeff = 3500.
		
		print(header['JD' + str(visit)], visit)
		# Prep Spectra
		aspec= np.reshape(spec,(1,len(spec)))
		aspecerr= np.reshape(specerr,(1,len(specerr)))
		cont= spec / continuum.fit(aspec,aspecerr,type='aspcap')[0]
		conterr = specerr / continuum.fit(aspec,aspecerr,type='aspcap')[0]
		shiftedSpec = bm.shiftFlux(cont, header['VHELIO' + str(visit)]) #if doesnt work try shifting after zero-ing
		cont[np.isnan(cont)] = 0.0
		conterr[np.isnan(conterr)] = 0.0

		# Prep model params
		params = constructParams(data)
		params = checkParams(params)
		restLambda = splot.apStarWavegrid()
		
		# Run grid
		for i in range(len(rangeTeff)):
			for j in range(len(rangeFluxRatio)):
				params = adjustParams(params, rangeTeff[i], rangeFluxRatio[j])
				binFlux = bm.binaryModelGen(locationID, apogeeID, params, visit, plot=plot)
				chi2[visit - 1][i][j] = ferre._chi2(binFlux,cont,conterr) / len(binFlux - 3)
				fn.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t\t{6}\n'.format(locationID, apogeeID, visit, round(params[0][0], 2), round(params[0][1], 2), round(params[6][1], 2), round(chi2[visit - 1][i][j],2 )))
				if (plot == True):
					BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
										[	[ restLambda, binFlux, 'blue', 'model' ],
											[ restLambda, cont, 'orange', 'unshifted' ],
											[ restLambda, shiftedSpec, 'green', 'shifted' ]],
											[params[0][0],params[0][1], params[6][1]], 'Delta V Shift', folder='grid_deltaVCheck')
	fn.close()
	inds = getMinIndicies(chi2)
	params = constructParams(data)
	return adjustParams(params, rangeTeff[inds[1]], rangeFluxRatio[inds[2]]), inds[0] + 1, chi2[inds[0]][inds[1]][inds[2]]
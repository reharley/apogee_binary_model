'''
Contains the grid and the helper functions that run the grid. Currently the grid only varies
the temperature of the secondary component of the binary and its flux. This will change
later and I may forget to update this summary.

An example of how the grid can be used is in RunGrid.py

The final results of the Grid can be found in lists/chi2.lis

With the individual target results found in lists/chi2/fieldID/2M_ID.lis

And if plot=True, then the plots can be found in plots/function/fieldID/2M_ID.png
'''
import os

import apogee.spec.plot as splot
import apogee.tools.read as apread
import numpy as np
from apogee.modelspec import ferre
from apogee.spec import continuum

import BinModelGen as bm
import BinPlot
from GridParam import GridParam
from Timer import Timer

def calcChi2(mspec,spec,specerr,weights=None):
	"""Internal function that calculates the chi^2 for a given model,
	 assumes that the wavelength axis==-1"""
	if not weights is None:
		return np.nansum(weights*(mspec-spec)**2./specerr**2,axis=-1)
	else:
		return np.nansum((mspec-spec)**2./specerr**2,axis=-1)

def getMinIndicies(x):
	'''
	Takes in a 3D array and finds the indicies of its minimum
	:param x: [in] The array to find the min for
	:return: The indicies as a tuple (ind1, ind2, ind3)
	'''
	inds = np.where(x == np.min(x))
	ind = [i[0] for i in inds]
	return ind

def targetGrid(gridParam, minimizedVisitParams, plot=True):
	'''
	The grid tests against ranging effective temperatures for both stars and the flux ratio of the
	secondary component. This is done by target.

	:param gridParam: [in/out] The GridParam of the target
	:param gridRes: [out] The visits that have the same paramters as the minimized chi2 visit
	:param plot: [in] If true makes plots to see intermediate steps (default=True)
	'''
	locationID = gridParam.locationID
	apogeeID = gridParam.apogeeID

	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	specs = apread.apStar(locationID, apogeeID, ext=1, header=False)
	specerrs = apread.apStar(locationID, apogeeID, ext=2, header=False)
	nvisits = header['NVISITS']

	# Prep model params
	gridParam.constructParams()

	# Prepare grid ranges
	rangeTeffA = np.arange(gridParam.minTeffA, gridParam.maxTeffA, gridParam.teffStepA)
	rangeTeffB = np.arange(gridParam.minTeffB, gridParam.maxTeffB, gridParam.teffStepB)
	rangeFluxRatio = np.arange(gridParam.minFluxRatio, gridParam.maxFluxRatio, gridParam.fluxStep)
	nrangeTeffA = len(rangeTeffA)
	nrangeTeffB = len(rangeTeffB)
	nrangeFluxRatio = len(rangeFluxRatio)

	# chi2 = np.full((nvisits, nrangeTeffA, nrangeTeffB, nrangeFluxRatio), -1.)
	#chi2 = np.full((nvisits, nrangeTeffA, nrangeTeffB, nrangeFluxRatio, nrangeRVA, nrangeRVB), -1.)
	ipg = ferre.Interpolator(lib='GK')
	ipf = ferre.Interpolator(lib='F')

	# Create file to store all the chi2 values
	path = 'lists/all_chi2/' + str(locationID) + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	fn = open(path + apogeeID + '.lis', 'w')
	fn.write(gridParam.toStringHeader())
	timer = Timer()
	timeSum = 0.0
	allChi2 = []
	for visit in range(1, nvisits + 1):
		timer.start()
		if (nvisits != 1):
			spec = specs[1+visit]
			specerr = specerrs[1+visit]
		else:
			spec = specs
			specerr = specerrs

		if (gridParam.modelParamA.rv is None):
			gridParam.getRVs(visit)
		
		rangeRVA = np.arange(gridParam.minRVA, gridParam.maxRVA, gridParam.rvAStep)
		rangeRVB = np.arange(gridParam.minRVB, gridParam.maxRVB, gridParam.rvBStep)
		nrangeRVA =len(rangeRVA)
		nrangeRVB =len(rangeRVB)
		
		chi2 = np.full((nrangeTeffA, nrangeTeffB, nrangeFluxRatio, nrangeRVA, nrangeRVB), -1.)
		print('Visit: ' + str(visit) ,'Grid dimensions: ' + str(chi2.shape))
		# Prep Spectra
		aspec= np.reshape(spec,(1, len(spec)))
		aspecerr= np.reshape(specerr,(1, len(specerr)))
		cont= spec / continuum.fit(aspec, aspecerr, type='aspcap')[0]
		conterr = specerr / continuum.fit(aspec, aspecerr, type='aspcap')[0]
		shiftedSpec = bm.shiftFlux(cont, header['VHELIO' + str(visit)])
		cont[np.isnan(cont)] = 0.0
		conterr[np.isnan(conterr)] = 0.0

		# Run grid
		for i in range(nrangeTeffA):
			gridParam.modelParamA.teff = rangeTeffA[i]
			componentA = bm.genComponent(gridParam.modelParamA, ipf, ipg)
			for j in range(nrangeTeffB):
				gridParam.modelParamB.teff = rangeTeffB[j]
				componentB = bm.genComponent(gridParam.modelParamB, ipf, ipg)
				for k in range(nrangeFluxRatio):
					componentBR = componentB * rangeFluxRatio[k]
					for l in range(nrangeRVA):
						componentAS = bm.shiftFlux(componentA, rangeRVA[l])
						for m in range(nrangeRVB):
							componentBS = bm.shiftFlux(componentBR, rangeRVB[m])
							binaryFlux = bm.combineFlux(componentAS, componentBS)
							chi2[i][j][k][l][m] = calcChi2(binaryFlux, shiftedSpec, conterr) / (len(binaryFlux) - 5)
							gridParam.chi2 = chi2[i][j][k][l][m]
							fn.write(gridParam.toString())
							if (plot is True):
								restLambda = splot.apStarWavegrid()
								BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
													[	[ restLambda, binaryFlux, 'blue', 'model' ],
														[ restLambda, cont, 'orange', 'unshifted' ],
														[ restLambda, shiftedSpec, 'green', 'shifted' ]],
														[gridParam.modelParamA.teff,gridParam.modelParamB.teff, gridParam.modelParamB.fluxRatio],
														'Delta V Shift', folder='grid_deltaVCheck')
		
		timeSum+=timer.end()
		allChi2.append(chi2)
	fn.close()
	ipg.close()
	ipf.close()

	print('Average visit time: ' + str(round(timeSum/nvisits, 2)) + str('s'))

	# Get minized values for each visit
	temp = np.array([GridParam(locationID, apogeeID) for i in range(nvisits)])
	indices = None
	for i in range(nvisits):
		inds = getMinIndicies(allChi2[i])
		temp[i].constructParams()
		temp[i].setParams(i + 1, rangeTeffA[inds[0]], rangeTeffB[inds[1]], rangeFluxRatio[inds[2]],
					rangeRVA[inds[3]], rangeRVB[inds[4]], allChi2[i][inds[0]][inds[1]][inds[2]][inds[3]][inds[4]])
		
		if (indices is None):
			indices = [i + 1, inds, allChi2[i][inds[0]][inds[1]][inds[2]][inds[3]][inds[4]]]
		if (allChi2[i][inds[0]][inds[1]][inds[2]][inds[3]][inds[4]] < indices[2]):
			indices = [i + 1, inds, allChi2[i][inds[0]][inds[1]][inds[2]][inds[3]][inds[4]]]

	minimizedVisitParams.append(temp)
	gridParam.constructParams()
	gridParam.setParams(indices[0], rangeTeffA[indices[1][0]], rangeTeffB[indices[1][1]], rangeFluxRatio[indices[1][2]],
					rangeRVA[indices[1][3]], rangeRVB[indices[1][4]], indices[2])
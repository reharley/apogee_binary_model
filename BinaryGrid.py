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
from GridParams import GridParams
from Timer import Timer
import os
import numpy as np
import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre
from apogee.spec import continuum

def getMinIndicies(x):
	'''
	Takes in a 3D array and finds the indicies of its minimum
	:param x: [in] The array to find the min for
	:return: The indicies as a tuple (ind1, ind2, ind3)
	'''
	index = np.argmin(x)
	inds = np.where(x == np.min(x))
	ind = [i[0] for i in inds]
	return ind

def targetGrid(gridParam,plot=True):
	'''
	The grid tests against ranging effective temperatures for both stars and the flux ratio of the secondary component.
	This is done by target.

	:param gridParam: [in/out] The GridParam of the target
	:param gridRes: [in] The amount of temperatures to test against within the range (default=5)
	:param plot: [in] If true makes plots to see intermediate steps (default=True)
	'''
	locationID = gridParam.locationID
	apogeeID = gridParam.apogeeID

	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	specs = apread.apStar(locationID, apogeeID, ext=1, header=False)
	specerrs = apread.apStar(locationID, apogeeID, ext=2, header=False)
	data = apread.apStar(locationID, apogeeID, ext=9, header=False)
	nvisits = header['NVISITS']

	# Prep model params
	gridParam.constructParams(data)
	
	# Prepare grid ranges
	rangeTeffA = np.arange(gridParam.minTeffA, gridParam.maxTeffA, gridParam.teffStepA)
	rangeTeffB = np.arange(gridParam.minTeffB, gridParam.maxTeffB, gridParam.teffStepB)
	rangeFluxRatio = np.arange(gridParam.minFluxRatio, gridParam.maxFluxRatio, gridParam.fluxStep)
	nrangeTeffA = len(rangeTeffA)
	nrangeTeffB = len(rangeTeffB)
	nrangeFluxRatio = len(rangeFluxRatio)

	chi2 = np.full((nvisits, nrangeTeffA, nrangeTeffB, nrangeFluxRatio), -1.)
	#chi2 = np.full((nvisits, nrangeTeffA, nrangeTeffB, nrangeFluxRatio, nrangeRVA, nrangeRVB), -1.)
	ipg = ferre.Interpolator(lib='GK')
	ipf = ferre.Interpolator(lib='F')
	
	print('Grid dimensions: ' + str(chi2.shape))
	# Create file to store all the chi2 values
	path = 'lists/chi2/' + str(locationID) + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	fn = open(path + apogeeID + '.lis', 'w')
	fn.write(gridParam.toStringHeader())
	timer = Timer()
	timeSum = 0.0
	for visit in range(1, nvisits + 1):
		timer.start()
		if (nvisits != 1):
			spec = specs[1+visit]
			specerr = specerrs[1+visit]
		else:
			spec = specs
			specerr = specerrs
		
		# Prep Spectra
		aspec= np.reshape(spec,(1,len(spec)))
		aspecerr= np.reshape(specerr,(1,len(specerr)))
		cont= spec / continuum.fit(aspec,aspecerr,type='aspcap')[0]
		conterr = specerr / continuum.fit(aspec,aspecerr,type='aspcap')[0]
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
					gridParam.modelParamB.fluxRatio = rangeFluxRatio[k]
					componentBR = componentB * rangeFluxRatio[k]
					gridParam.getRVs(visit)
					componentAS = bm.shiftFlux(componentA, gridParam.modelParamA.rv)
					componentBS = bm.shiftFlux(componentBR, gridParam.modelParamB.rv)
					binaryFlux = bm.combineFlux(componentAS, componentBS)
					chi2[visit - 1][i][j][k] = ferre._chi2(binaryFlux,cont,conterr) / (len(binaryFlux) - 5)
					fn.write(gridParam.toString())
					if (plot == True):
						restLambda = splot.apStarWavegrid()
						BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
											[	[ restLambda, binFlux, 'blue', 'model' ],
												[ restLambda, cont, 'orange', 'unshifted' ],
												[ restLambda, shiftedSpec, 'green', 'shifted' ]],
												[gridParam.modelParamA.teff,gridParam.modelParamB.teff, gridParam.modelParamB.fluxRatio],
												'Delta V Shift', folder='grid_deltaVCheck')
		timeSum+=timer.end()
	fn.close()
	ipg.close()
	ipf.close()
	
	print('Average visit time: ' + str(round(timeSum/nvisits, 2)) + str('s'))

	# Get minized values
	inds = getMinIndicies(chi2)
	gridParam.constructParams(data)
	gridParam.setParams(inds[0] + 1, rangeTeffA[inds[1]],rangeTeffB[inds[2]], rangeFluxRatio[inds[3]],
					gridParam.modelParamA.rv, gridParam.modelParamB.rv, chi2[inds[0]][inds[1]][inds[2]][inds[3]])
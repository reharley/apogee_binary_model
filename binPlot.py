'''
Binary Plot Module

Contains all plotting routines to plot our binaries and other various plots.
All plots will be sent to the immediate subdirectory './plots/'.
'''
import matplotlib.pyplot as plt
import numpy as np
import os

def plotDeltaVCheck(gridParam, visit, model, title, range=[16650, 16800], folder='deltaV_check', dpi=None):
	'''
	Creates the plot to generate a visual aid in checking the doppler shift on the binary.
	The plot is saved in './plots/deltaV_check/locationID/apogeeID/'

	Example:
		binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
							[[ restLambda, mspec[0], 'blue', 'rest model specA' ],
							 [ restLambda, mspec[1], 'green', 'rest model specB' ],
							 [ restLambda, cspec, 'orange', 'cont-norm spec' ],
							 [ restLambda, shiftedFlux, 'purple', 'shift model specA' ]],
							[ params[0][1], params[0][1]], 'Delta V Shift')

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:param plots: A multi-dimensional array containing the arguments for plt.plot. Format in example
	:param params: Relevant parameters the model was generated with. format: [ Teff1, Teff2, FluxRatio ]
	:param title: The title of the figure
	:param range: The range to limit the plot by (default=[16650, 16800])
	:param folder: The folder to save the plot in (default='deltaV_check')
	:param dpi: The resolution in dots per inch. If None it will default to the value. 
		For more details: http://matplotlib.org/api/pyplot_api.html?highlight=savefig#matplotlib.pyplot.savefig
	'''
	locationID = gridParam.locationID
	apogeeID = gridParam.apogeeID

	# Generate the wavelength grid
	restLambda = splot.apStarWavegrid()
	plots = [[restLambda, model, 'blue', 'model'],
			[restLambda, gridParam.spec, 'orange', 'obs']]
	# Create path
	path = 'plots/' + folder + '/' + str(locationID) + '/' + apogeeID + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	
	table = 'Teff A: ' + str(int(gridParam.modelParamA.teff)) + '|  Teff B: ' + str(int(gridParam.modelParamB.teff)) + '\n' \
			'logg A: ' + str(gridParam.modelParamA.logg) + '|      logg B: ' + str(gridParam.modelParamB.logg) + '\n' \
			'metals A: ' + str(gridParam.modelParamA.metals) + '|  metals B: ' + str(gridParam.modelParamB.metals) + '\n' \
			'[A/M] A: ' + str(gridParam.modelParamA.alphafe) + '|    [A/M] B: ' + str(gridParam.modelParamB.alphafe) + '\n' \
			'[N/M] A: ' + str(gridParam.modelParamA.nfe) + '|    [N/M] B: ' + str(gridParam.modelParamB.nfe) + '\n' \
			'[C/M] A: ' + str(gridParam.modelParamA.cfe) + '|    [C/M] B: ' + str(gridParam.modelParamB.cfe) + '\n'

	fig = plt.figure()
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)

	# Plot each spectrum
	for plot in plots:
		ax.plot(plot[0], plot[1], color=plot[2], label=plot[3])
	
	# Create labels/handles
	handles, labels = ax.get_legend_handles_labels()
	ax.legend(handles, labels, loc='best')
	ax.
	ax.set_ylabel(r'$f/f_c(\lambda)$')
	ax.set_xlabel(r'$\lambda - \AA$')
	if (range != None):
		ax.set_xlim(range[0], range[1])
	plt.title(title, loc='left')
	ax.text(0, 0.95, str(locationID) + ', ' + apogeeID + '    Visit: ' + str(visit), ha='left', transform=ax.transAxes)
	ax.text(0.99, .67, table, ha='right', va='bottom', transform=ax.transAxes)
	plt.savefig(path + str(visit) +  '.png', format='png', dpi=dpi)
	plt.clf()
	plt.close('all')

def plotDeltaVCheck(locationID, apogeeID, visit, plots, params, title, range=[16650, 16800], folder='deltaV_check', dpi=None):
	'''
	Creates the plot to generate a visual aid in checking the doppler shift on the binary.
	The plot is saved in './plots/deltaV_check/locationID/apogeeID/'

	Example:
		binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
							[[ restLambda, mspec[0], 'blue', 'rest model specA' ],
							 [ restLambda, mspec[1], 'green', 'rest model specB' ],
							 [ restLambda, cspec, 'orange', 'cont-norm spec' ],
							 [ restLambda, shiftedFlux, 'purple', 'shift model specA' ]],
							[ params[0][1], params[0][1]], 'Delta V Shift')

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:param plots: A multi-dimensional array containing the arguments for plt.plot. Format in example
	:param params: Relevant parameters the model was generated with. format: [ Teff1, Teff2, FluxRatio ]
	:param title: The title of the figure
	:param range: The range to limit the plot by (default=[16650, 16800])
	:param folder: The folder to save the plot in (default='deltaV_check')
	:param dpi: The resolution in dots per inch. If None it will default to the value. 
		For more details: http://matplotlib.org/api/pyplot_api.html?highlight=savefig#matplotlib.pyplot.savefig
	'''
	# Create path
	path = 'plots/' + folder + '/' + str(locationID) + '/' + apogeeID + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)

	# Plot each spectrum
	for plot in plots:
		ax.plot(plot[0], plot[1], color=plot[2], label=plot[3])
	
	# Create labels/handles
	handles, labels = ax.get_legend_handles_labels()
	ax.legend(handles, labels, loc='best')

	ax.set_ylabel(r'$f/f_c(\lambda)$')
	ax.set_xlabel(r'$\lambda - \AA$')
	if (range != None):
		ax.set_xlim(16650, 16800)
	plt.title(title, loc='left')
	ax.text(0, 0.95, str(locationID) + ', ' + apogeeID + '    Visit: ' + str(visit), ha='left', transform=ax.transAxes)
	if (len(params) < 3):
		plt.savefig(path + str(visit) +  '_' + str(int(params[0])) + '_' + str(int(params[1])) + '.png', format='png', dpi=dpi)
	else:
		plt.savefig(path + str(visit) +  '_' + str(int(params[0])) + '_' + str(int(params[1])) + '_' + str(round(params[2], 2)) + '.png', format='png', dpi=dpi)
	plt.clf()
	plt.close('all')

def plotCOMPCCF(locationID, apogeeID, visit, shift, plots, params, normed, folder='CCF'):
	'''
	Generates the CCF plots in normalized and unormalized stages.
	The plot is saved in './plots/CCF/locationID/apogeeID/'

	Example:
		binPlot.plotCCF(locationID, apogeeID, visit, restLambda, pixelNorm, params, 'norm')

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:param restLambda: Wavelength grid to use for the x axes
	:param y: The output of the numpy.correlate function
	:param params: The paramters to test against the observed data.
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	:param normed: string to put in filename to indicate whether normed or not. See example for use.
	:return:
	'''
	# Create path
	path = 'plots/' + folder + '/' + str(locationID) + '/' + apogeeID + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	
	fig = plt.figure()
	plt.title('CCF')
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)
	
	for plot in plots:
		ax.plot(plot[0], color=plot[1], label=plot[2])

	ax.set_xlabel('CCF Indicies')
	ax.set_ylabel('Agreement')
	ax.text(0, 0.95, str(locationID) + ', ' + apogeeID + '    Visit: ' + str(visit) + ' shift (km/s): ' + str(shift), ha='left', transform=ax.transAxes)
	handles, labels = ax.get_legend_handles_labels()
	ax.legend(handles, labels, loc='center right')
	plt.savefig(path + '_' + normed + str(visit) + '.png', format='png')
	plt.clf()
	plt.close('all')

def plotCCF(locationID, apogeeID, visit, ccf, params, normed, folder='CCF'):
	'''
	Generates the CCF plots in normalized and unormalized stages.
	The plot is saved in './plots/CCF/locationID/apogeeID/'

	Example:
		binPlot.plotCCF(locationID, apogeeID, visit, restLambda, pixelNorm, params, 'norm')

	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:param restLambda: Wavelength grid to use for the x axes
	:param y: The output of the numpy.correlate function
	:param params: The paramters to test against the observed data.
		format: [ [Teff1, ...], [logg1, ...], [metals1, ...], [am1, ...], [nm1, ...], [cm1, ...]]
	:param normed: string to put in filename to indicate whether normed or not. See example for use.
	:return:
	'''
	# Create path
	path = 'plots/' + folder + '/' + str(locationID) + '/' + apogeeID + '/'
	if not os.path.exists(path):
		os.makedirs(path)

	
	table = 'Teff A: ' + str(int(params[0][0])) + '|  Teff B: ' + str(int(params[0][1])) + '\n' \
			'logg A: ' + str(params[1][0]) + '|      logg B: ' + str(params[1][1]) + '\n' \
			'metals A: ' + str(params[2][0]) + '|  metals B: ' + str(params[2][1]) + '\n' \
			'[A/M] A: ' + str(params[3][0]) + '|    [A/M] B: ' + str(params[3][1]) + '\n' \
			'[N/M] A: ' + str(params[4][0]) + '|    [N/M] B: ' + str(params[4][1]) + '\n' \
			'[C/M] A: ' + str(params[5][0]) + '|    [C/M] B: ' + str(params[5][1]) + '\n'
			
	
	fig = plt.figure()
	plt.title('CCF Plots')
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)
	
	ax.plot(ccf)
	ax.set_xlabel('CCF Indicies')
	ax.set_ylabel('Agreement')
	ax.text(0, 0.95, str(locationID) + ', ' + apogeeID + '    Visit: ' + str(visit), ha='left', transform=ax.transAxes)
	ax.text(0.99, .67, table, ha='right', va='bottom', transform=ax.transAxes)
	plt.savefig(path + '_' + normed + str(visit) + '.png', format='png')
	plt.clf()
	plt.close('all')

def plotTeffGrid(locationID, apogeeID, visit, rangeTeff, grid, title, folder='teffGrids'):
	'''
	Generates the Teff grid plot as a visual aid to see any correlations between the temperature and whatever values are
	inside of grid.
	The plot is saved in './plots/teffGrids' + title + '/locationID/apogeeID/'

	Example:
		plotTeffGrid(locationID, apogeeID, visit, rangeTeff, peak, 'CCF')
	:param locationID: The location ID of the binary.
	:param apogeeID: The apogee ID of the binary.
	:param visit: The visit we are using to test against.
	:param rangeTeff: The temperature range we are testing against
	:param grid: The grid to plot to plt.pcolor
	:param title: The title of the figure
	'''
	# Create path
	path = 'plots/' + folder + title + '/' + str(locationID) + '/' + apogeeID + '/'
	if not os.path.exists(path):
		os.makedirs(path)
	
	# Get known values of stars
	# locationIDs, apogeeIDs, data[2], data[3] = np.loadtxt('known_values.dat', delimiter=',', dtype=str,skiprows=1)
	data = np.loadtxt('lists/known_values.dat', delimiter=',', dtype=str,skiprows=1)
	rows = np.where(data[1] == apogeeID)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)

	#plot known stars
	try:
		for row in rows:
			ax.plot(float(data[row][2][0]), float(data[row][3][0]), marker='*', ms=10)
			ax.plot(float(data[row][3][0]), float(data[row][2][0]), marker='*', ms=10)
	except IndexError:
		pass
	
	plt.pcolor(rangeTeff, rangeTeff, grid, cmap='RdBu')
	plt.colorbar(label='Cross Correlation function magnitudes')
	plt.xlabel('Model Teff')
	plt.ylabel('Model Teff')
	plt.title('Teff Grid ' + title, loc='left')
	ax.text(0, 0.95, str(locationID) + ', ' + apogeeID + '    Visit: ' + str(visit), ha='left', transform=ax.transAxes)
	plt.savefig(path + str(int(rangeTeff[0])) + '_' + str(int(rangeTeff[len(rangeTeff) - 1])) + '_' + str(visit) + '.png', format='png')
	plt.clf()
	plt.close('all')
# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import binPlot
import BinModelGen as bm
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

def checkParams(params):
	if (params[0] >= 6000.):
		params[0] = 5500.
	if (params[0] <= 3500.):
		params[0] = 3500.
	if (params[1] >= 5.0):
		params[1] = 4.9
	
	return params

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

locationIDs, apogeeIDs = np.loadtxt('lists/binaries3.dat', unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
shift = [ 	[0.0, False],  #shift of 1  (km/s) #Works well for Visit 4,6 (note from Jess)
			[0.0, False], #shift of 3 (km/s) #Works well! (Note from Jess)
			[0.0, False]  ]#shift of 4 (km/s)

f = open('lists/chi2.lis', 'w')
f.write('{0}\t{1}\t\t{2}\t{3}\n'.format('Field ID', '2MID', 'visit', 'chi2'))
for i in range(len(locationIDs)):
	if (shift[i][1] == True):
		continue
	
	locationID = locationIDs[i]
	apogeeID = apogeeIDs[i]
	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
	specs = apread.apStar(locationID, apogeeID, ext=1, header=False)
	specerrs = apread.apStar(locationID, apogeeID, ext=2, header=False)
	data = apread.apStar(locationID, apogeeID, ext=9, header=False)
	nvisits = header['NVISITS']
	print('Plotting: ' + locationIDs[i] + ', ' + apogeeIDs[i] + ', nvisits: ' + str(nvisits))
	print(str(i + 1) + '/' + str(targetCount) + ' targets completed')
	for visit in range(1, nvisits):
		if (nvisits != 1):
			spec = specs[1+visit]
			specerr = specerrs[1+visit]
		else:
			spec = specs
			specerr = specerrs
		
		print(header['JD' + str(visit)], visit)
		aspec= np.reshape(spec,(1,len(spec)))
		aspecerr= np.reshape(specerr,(1,len(specerr)))
		cont= spec / continuum.fit(aspec,aspecerr,type='aspcap')[0]
		params = [ 	data['TEFF'][0],	# effective temperature
					data['LOGG'][0],	# surface gravity
					data['FEH'][0],		# metal abundance
					data['ALPHA'][0],  	# α element
					0.0,           		# nitrogen relative abundance
					data['CARBON'][0]]	# carbon relative abundance
		
		params = checkParams(params)
		
		# Generate models (flux1, flux2)
		mspec = ferre.interpolate(params[0], params[1], params[2],
									params[3], params[4], params[5])

		restLambda = splot.apStarWavegrid()
		binFlux = bm.binaryModelGen(locationID, apogeeID, params, visit)
		shiftedSpec = bm.shiftFlux(cont, header['VHELIO' + str(visit)])

		chi2 = ferre._chi2(binFlux, cont, specerr)
		f.write('{0}\t{1}\t{2}\t{3}\n'.format(locationID, apogeeID, visit, chi2))


		binPlot.plotDeltaVCheck(locationID, apogeeID, visit,
							[	[ restLambda, binFlux, 'blue', 'model' ],
								[ restLambda, cont, 'orange', 'unshifted' ],
								[ restLambda, shiftedSpec, 'green', 'shifted' ]],
								[0.0,0.0], 'Delta V Shift', folder='binModelGen_test')
f.close()
gifGen('binModelGen_test')
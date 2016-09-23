# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import emcee
import numpy as np
import BinModelGen as bm
from apogee.spec import continuum
from apogee.modelspec import ferre
import apogee.tools.read as apread
from GridParam import GridParam
from Grid import writeGridToFile
import os
from matplotlib import pyplot as plt
from Queue import Queue
import time
from multiprocessing import Process
from Timer import Timer

def calcChi2(mspec,spec,specerr,weights=None):
	"""Internal function that calculates the chi^2 for a given model,
	 assumes that the wavelength axis==-1"""
	if not weights is None:
		return np.nansum(weights*(mspec-spec)**2./specerr**2,axis=-1)
	else:
		return np.nansum((mspec-spec)**2./specerr**2,axis=-1)

def MCMC(gridParam, nWalkers=20, nDim=5, threads=4, nSteps=10):
	position = np.full((nWalkers, nDim), 0.0)
	for i in range(nWalkers):
		position[i][0] = gridParam.modelParamA.teff + (4000. * np.random.randn(1))
		position[i][1] = gridParam.modelParamB.teff + (4000. * np.random.randn(1))
		position[i][2] = 1.0 + np.random.randn(1)
		position[i][3] = gridParam.modelParamA.rv + (25.0 * np.random.randn(1))
		position[i][4] = gridParam.modelParamB.rv + (25.0 * np.random.randn(1))
	
	sampler = emcee.EnsembleSampler(nWalkers, nDim, fitModel, args=[gridParam], threads=threads)
	sampler.run_mcmc(position, nSteps)
	return sampler

def fitModel(guess, gridParam):
	if not guess is None:
		gridParam.modelParamA.teff = guess[0]
		gridParam.modelParamB.teff = guess[1]
		gridParam.modelParamB.fluxRatio = guess[2]
		gridParam.modelParamA.rv = guess[3]
		gridParam.modelParamB.rv = guess[4]
	
	ipf, ipg = ferre.Interpolator(lib='F'), ferre.Interpolator(lib='GK')
	componentA = bm.genComponent(gridParam.modelParamA, ipf, ipg)
	componentB = bm.genComponent(gridParam.modelParamB, ipf, ipg)
	componentBR = componentB * gridParam.modelParamB.fluxRatio
	componentAS = bm.shiftFlux(componentA, gridParam.modelParamA.rv)
	componentBS = bm.shiftFlux(componentBR, gridParam.modelParamB.rv)
	ipf.close()
	ipg.close()

	# Combine the flux as a binary
	binaryFlux = bm.combineFlux(componentAS, componentBS)

	gridParam.chi2 = calcChi2(binaryFlux, gridParam.spec, gridParam.specErr) / (len(binaryFlux) - 5.0)
	return -1.0 * gridParam.chi2

def runTarget(gridParam):
	locationID = gridParam.locationID
	apogeeID = gridParam.apogeeID

	badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True, dr='13')
	specs = apread.apStar(locationID, apogeeID, ext=1, header=False, dr='13')
	specerrs = apread.apStar(locationID, apogeeID, ext=2, header=False, dr='13')
	nvisits = header['NVISITS']
	gridParamVists = []
	for visit in range(1, nvisits + 1):
		print('Visit ' + str(visit) + '/' + str(nvisits))
		if nvisits is 1:
			spec = specs
			specerr = specerrs
		else:
			spec = specs[1 + nvisits]
			specerr = specerrs[ 1+ nvisits]
		
		aspec= np.reshape(spec,(1, len(spec)))
		aspecerr= np.reshape(specerr,(1, len(specerr)))
		cont= spec / continuum.fit(aspec, aspecerr, type='aspcap')[0]
		conterr = specerr / continuum.fit(aspec, aspecerr, type='aspcap')[0]
		
		gridParam = GridParam(locationID, apogeeID)
		gridParam.constructParams()
		gridParam.spec = bm.shiftFlux(cont, header['VHELIO' + str(visit)])
		gridParam.specErr = bm.shiftFlux(conterr, header['VHELIO' + str(visit)])
		gridParam.getRVs(visit)

		nSteps = 100
		sampler = MCMC(gridParam, nSteps=nSteps)
		circular_samples = sampler.chain[:, :, :].reshape((-1, 5))
		results = np.asarray(list(map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
							zip(*np.percentile(circular_samples, [16, 50, 84], axis=0)))))
		
		fig, ax = plt.subplots(5, 1, sharex='col')
		for i in range(5):
			for j in range(len(sampler.chain[:, 0, i])):
				ax[i].plot(np.linspace(0, nSteps, num=nSteps), sampler.chain[j, :, i], 'k', alpha=0.2)
			ax[i].plot(np.linspace(0, nSteps, num=nSteps) , np.ones(nSteps)*results[i][0], 'b', lw=2)
		fig.set_figheight(20)
		fig.set_figwidth(15)
		if not os.path.exists('plots/walker/' + str(locationID) + '/' + str(apogeeID) + '/'):
			os.makedirs('plots/walker/' + str(locationID) + '/' + str(apogeeID) + '/')
		plt.savefig('plots/walker/' + str(locationID) + '/' + str(apogeeID) + '/' + str(visit) + '.png')

		plt.close('all')
		gridParam.modelParamA.teff = results[0][0]
		gridParam.modelParamB.teff = results[1][0]
		gridParam.modelParamB.fluxRatio = results[2][0]
		gridParam.modelParamA.rv = results[3][0]
		gridParam.modelParamB.rv = results[4][0]

		gridParam.chi2 = -1.0 * fitModel(None, gridParam)
		gridParamVists.append(gridParam)
	

	if not os.path.exists('lists/chi2/' + str(locationID) + '/'):
		os.makedirs('lists/chi2/' + str(locationID) + '/')
	filename = 'lists/chi2/' + str(locationID) + '/' + str(apogeeID) + '.tbl'
	writeGridToFile(gridParamVists, filename=filename)

filename='lists/binaries3.dat'

locationIDs, apogeeIDs = np.loadtxt(filename, unpack=True, delimiter=',', dtype=str)
targetCount = len(locationIDs)
targets = np.array([(GridParam(locationIDs[i], apogeeIDs[i])) for i in range(targetCount)])


'''procs = [Process(target=runTarget, args=(targets[0],)), Process(target=runTarget, args=(targets[1],)),
		Process(target=runTarget, args=(targets[2],))]#, Process(target=runTarget, args=(targets[3],))]
timers = [Timer(), Timer(), Timer()]#, Timer()]
for i in range(3):
	procs[i].start()
	timers[i].start()

running = True
visitSum = 0.0
while running:
	for i in range(3):
			if procs[i].is_alive() == False:
				badheader, header = apread.apStar(locationIDs[i], apogeeIDs[i], ext=0, header=True, dr='13')
				nvisits = header['NVISITS']
				visitSum+= timers[i].end() / nvisits
	if procs[0].is_alive() == False and procs[1].is_alive() == False and procs[2].is_alive() == False:
		running = False
	time.sleep(2)'''
timer = Timer()
visitSum = 0.0
badheader, header = apread.apStar(locationIDs[i], apogeeIDs[i], ext=0, header=True, dr='13')
nvisits = header['NVISITS']
runTarget(targets[0])
visitSum+= timer.end() / nvisits
print('avg visit time:', visitSum/targetCount)

'''
done=4
print('------------Target ' + str(done + 1) + '/' + str(targetCount) + ' ------------')
while targetQueue.empty() == False:
	# runTarget(targetQueue.get_nowait())
	for i in range(4):
		if procs[i].is_alive() == False:
			del(procs[i])
			if targetQueue.empty() == False:
				procs.append(Process(target=runTarget, args=(targetQueue.get_nowait(),)))
				procs[3].start()
			done+=1
			print('------------Target ' + str(done + 1) + '/' + str(targetCount) + ' ------------')
	time.sleep(20)'''
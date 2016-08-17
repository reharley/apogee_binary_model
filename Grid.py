from Timer import Timer
from GridParams import GridParams
import BinaryGrid as bg
import numpy as np
import apogee.tools.read as apread
import os

def checkPreviousData(gridParams, filename='lists/chi2.lis'):
	'''
	Checks for targets that have already been chi2 minimized.

	:param gridParams: List of GridParams containing the targets parameters
	:param filename: File to check for minimized chi2 values (default='lists/chi2.lis')
	'''
	# Check for previous fitted data
	apogChi2s_file = teffAs_file = teffBs_file = fluxRatios_file = np.array([])
	if (os.path.isfile(filename) == True):
		apogChi2s_file, teffAs_file, teffBs_file, fluxRatios_file, chi2_file = np.loadtxt(filename, unpack=True, skiprows=1, usecols=[1, 3, 4, 5, 9], delimiter=None, dtype=str)
		print(teffBs_file)
		if (apogChi2s_file.size > 0):
			for i, apogeeID in enumerate(apogeeIDs):
				index = np.where(apogChi2s_file == apogeeID)[0]
				# gridParams[i].setParams(0, float(teffAs_file[index]), float(teffBs_file[index]), float(fluxRatios_file[index]), )

def cleanSubdirs(subdirs):
	'''
	Quick function to check for .DS_Store on Mac

	:param subdirs: The subdir to check for .DS_Store
	:return: New list of sub-directories without the .DS_Store file
	'''
	if subdirs[0] == '.DS_Store':
		return subdirs[1:]
	return subdirs

def gatherChi2Reports(folder='lists/chi2/'):
	'''
	Gathers minimized chi2 paramaters to report in a corresponding lists/chi2.lis file in the case of the grid not being
	able to complete.
	:param folder:
	'''
	oldDir = os.getcwd()
	os.chdir(folder)
	subdirs = cleanSubdirs(os.listdir('.'))
	for subdir in subdirs:
		file_names = sorted((fn for fn in cleanSubdirs(os.listdir(subdir)) if fn.endswith('.png')))
		for fn in file_names:
			print(fn)

def grid(passCount, gridParams):
	'''
	The binary model fitting grid. This function will fit the targets of the following parameters:
	 	1) Teff of component A
	 	2) Teff of component B
	 	3) Flux Ratio of component B
	 	4) Relative Heliocentric Velocity of Component A
	 	5) Relative Heliocentric Velocity of Component B

	After chi2 minimization of the above parameters, the parameters used to get the minimized chi2 value is written into
	lists/chi2.lis. The other parameters that were tested on the grid and their corresponding chi2 values can be found
	in lists/chi2/FIELD_ID/2M_ID.lis.

	:param passCount: [in] The amount of maximum amount of passes the grid will go through
	:param gridParams: [in/out] The list of GridParams that contain the targets fitting data (built in runGrid)
	'''
	targetCount = len(gridParams)
	tpass = Timer()
	tpassSum = 0.0
	for j in range(passCount):
		tpass.start()
		print('-------------PASS ' + str(j+1) + '/' + str(passCount) + '-------------')
		ttarget = Timer()
		ttargetSum = 0.0
		for i in range(targetCount):
			locationID = gridParams[i].locationID
			apogeeID = gridParams[i].apogeeID
			badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)
			nvisits = header['NVISITS']
			print('Fitting: ' + locationID + ', ' + apogeeID + ', nvisits: ' + str(nvisits))
			print('On target: ' + str(i+1) + '/' + str(targetCount))
			ttarget.start()
			
			bg.targetGrid(gridParams[i], plot=False)
			
			temp = ttarget.end()
			ttargetSum+= temp
			print('Target run time: ' + str(round(temp, 2)))
		temp = ttarget.end()
		ttargetSum+= temp
		print('Pass run time: ' + str(round(temp, 2)) + str('s'))
		print('Average target run time: ' + str(round(ttargetSum/targetCount, 2)) + str('s'))
	print('Average target run time: ' + str(round(tpassSum/passCount, 2)) + str('s'))

def writeGridToFile(gridParams, filename='lists/chi2.lis'):
	'''
	Takes in the list of targets grid parameters and writes them to the master chi2 file in lists/chi2.lis.

	:param gridParams: [in] The list of GridParams for each target
	:param filename: [in] The filename of the master chi2 file (default='lists/chi2')
	'''
	targetCount = len(gridParams)
	f = open(filename, 'w')
	f.write(gridParams[0].toStringHeader())
	for i in range(targetCount):
		f.write(gridParams[i].toString())
	f.close()

def runGrid(passCount, filename='lists/binaries3.dat'):
	'''
	Wrapper function to run the binary mofel fitting grid.

	:param passCount: [in] The maximum amount of passes to run on the grid
	:param filename: [in] The filename of the file containing a list of targets field and APOGEE ID's to use
	'''
	# Prep Grid
	locationIDs, apogeeIDs = np.loadtxt(filename, unpack=True, delimiter=',', dtype=str)
	targetCount = len(locationIDs)
	gridParams = np.array([GridParams(apogeeIDs[i],locationIDs[i]) for i in range(targetCount)])
	# Use past results
	# checkPreviousData(gridParams)

	grid(passCount, gridParams)
	writeGridToFile(gridParams)
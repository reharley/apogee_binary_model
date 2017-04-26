# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()


import apogee.tools.read as apread
from Timer import Timer
from BFData import *
from BinFinderTools import *

filename = 'lists/binaries2.dat'
#filename = '/Volumes/CoveyData-1/APOGEE_Spectra/APOGEE2_DR13/Bisector/BinaryFinder4/interestingTargetsDualPeak.csv'

locationIDs, apogeeIDs = np.loadtxt(filename, delimiter=',',unpack=True, dtype=str,skiprows=1)
print('starting')
genPeakHCutTable(locationIDs, apogeeIDs, 'rTable')
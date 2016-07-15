# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()


import apogee.tools.read as apread
import apogee.spec.plot as splot
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.stats import pearsonr

teff1 = 5000.
teff2 = 5250.
logg = 4.7
metals = am = nm = cm = 0.

locationID = 4611
apogeeID = '2M05350392-0529033'
spec, hdr= apread.apStar(locationID,apogeeID,ext=1)

# mspec1= ferre.interpolate(teff1,logg,metals,am,nm,cm)
# mspec2= ferre.interpolate(teff2,logg,metals,am,nm,cm)
# print(mspec1.shape)
# print(pearsonr(mspec1, mspec2))
spec[0][spec[0] <= 0.] = np.nan

nan_vals = [i for i in range(len(spec[0])) if np.isnan(spec[0][i])]
nan_ranges = [(nan_vals[i] + 1, nan_vals[i+1]) for i in range(len(nan_vals) - 1) if nan_vals[i+1]!=nan_vals[i]+1]


print(nan_ranges)
# print(spec[0][0:nan_ranges[0][0]])

'''ms1 = np.array(mspec1[np.isnan(mspec1) == False])
ms2 = np.array(mspec2[np.isnan(mspec2) == False])
print(np.corrcoef(mspec1, mspec2))
for i in range(len(ms1)):
	if np.isnan(ms1[i]) or np.isnan(ms2[i]):
		print(i, ms1[i], ms2[i])'''
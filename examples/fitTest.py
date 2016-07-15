# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()


import apogee.tools.read as apread
import apogee.spec.plot as splot
from apogee.modelspec import ferre
import matplotlib.pyplot as plt
import numpy as np

teff1 = 5000.
teff2 = 5250.
logg = 4.7
metals = am = nm = cm = 0.

locationID = 4611
apogeeID = '2M05350392-0529033'

'''spec, hdr = apread.apStar(locationID,apogeeID,ext=1)
err, hdr = apread.apStar(locationID, apogeeID, ext=2)

# Clean the zero's
spec[0][spec[0] <= 0.] = np.nan

nan_vals = [i for i in range(len(spec[0])) if np.isnan(spec[0][i])]
nan_ranges = [(nan_vals[i] + 1, nan_vals[i+1]) for i in range(len(nan_vals) - 1) if nan_vals[i+1]!=nan_vals[i]+1]

print(nan_ranges)
specChunk = spec[0][nan_ranges[0][0]:nan_ranges[0][1]]
errChunk = err[0][nan_ranges[0][0]:nan_ranges[0][1]]'''

aspec= apread.apStar(locationID, apogeeID, ext=1, header=False)[1]
aspecerr= apread.apStar(locationID, apogeeID, ext=2, header=False)[1]
# Input needs to be (nspec,nwave)
aspec= np.reshape(aspec,(1,len(aspec)))
aspecerr= np.reshape(aspecerr,(1,len(aspecerr)))
# Fit the continuum
from apogee.spec import continuum
cont= continuum.fit(aspec,aspecerr,type='aspcap')

cspec= apread.aspcapStar(locationID, apogeeID,ext=1,header=False)
import apogee.spec.plot as splot
splot.waveregions(aspec[0]/cont[0])
splot.waveregions(cspec,overplot=True)

'''params = ferre.fit(locationID, apogeeID,
							teff=teff1, fixteff=True,
							logg=logg, fixlogg=True,
							metals=metals, fixmetals=False,
							am=am, fixam=False,
							nm=nm, fixnm=False,
							cm=cm, fixcm=False,
							verbose=True)
'''

'''mspec1= ferre.interpolate(params[0][1],params[0][2],params[0][3],params[0][4],params[0][5],params[0][6])
splot.waveregions(locationID, apogeeID)
splot.waveregions(mspec1, overplot=True)'''
plt.draw()
plt.show()
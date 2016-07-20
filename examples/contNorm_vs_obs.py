# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import apogee.spec.plot as splot
import matplotlib.pyplot as plt
import numpy as np

locationID = 4611
apogeeID = '2M05350392-0529033'
rMin, rMax = 16740., 16820.


restLambda = splot.apStarWavegrid()
ind = np.argwhere(np.logical_and(restLambda > rMin, restLambda < rMax))
rMin, rMax = ind[0], ind[-1]

# Get the continuum-normalized spectrum
cspec = apread.aspcapStar(locationID, apogeeID, ext=1, header=False)
# Get visit 1
spec = apread.apStar(locationID, apogeeID, ext=1, header=False)[3]
spec[np.isnan(spec)] = 0.
specNorm = spec[rMin:rMax] / spec[rMin:rMax].max(axis=0)

# compare
plt.plot(restLambda[rMin:rMax], cspec[rMin:rMax])
plt.plot(restLambda[rMin:rMax], specNorm)
plt.draw()
plt.show()
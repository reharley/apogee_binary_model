# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import apogee.spec.plot as splot
import matplotlib.pyplot as plt

locationID = 4611
apogeeID = '2M05350392-0529033'
# spec, hdr= apread.apStar(locationID,apogeeID,ext=2)
# print(spec.shape)
# print(list(spec[0]))
splot.waveregions(locationID, apogeeID)
# plt.plot(spec[0])
fig = plt.gcf()
fig.set_size_inches(30.0, 15.0, forward=True)
plt.draw()
plt.show()
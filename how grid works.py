import apogee.spec.plot as splot
import apogee.tools.read as apread
import numpy as np
from apogee.modelspec import ferre
from apogee.spec import continuum
import apogee.spec.plot as splot
import matplotlib.pyplot as plt

import BinModelGen as bm
import BinPlot
from BinaryGrid import calcChi2
from GridParam import GridParam
from Timer import Timer

locationID = 4586
apogeeID = '2M03441568+3231282'
restLambda = splot.apStarWavegrid()
visit = 1

badheader, header = apread.apStar(locationID, apogeeID, ext=0, header=True)

gridParam = GridParam(locationID, apogeeID)
gridParam.constructParams()

spec = apread.apStar(locationID, apogeeID, ext=1, header=False)[1 + visit]
specerr = apread.apStar(locationID, apogeeID, ext=2, header=False)[1 + visit]
# plt.plot(restLambda, spec)

aspec = np.reshape(spec,(1, len(spec)))
aspecerr = np.reshape(specerr,(1, len(specerr)))
cont = spec / continuum.fit(aspec, aspecerr, type='aspcap')[0]
conterr = specerr / continuum.fit(aspec, aspecerr, type='aspcap')[0]
shiftedSpec = bm.shiftFlux(cont, header['VHELIO' + str(visit)])
conterr = bm.shiftFlux(cont, header['VHELIO' + str(visit)])
BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, cont, 'blue', 'Data']],
						[gridParam.modelParamA.teff, gridParam.modelParamB.teff], '', folder='model_gen')
# plt.plot(restLambda, cont)
# plt.show()
ipg = ferre.Interpolator(lib='GK')
ipf = ferre.Interpolator(lib='F')

componentA = bm.genComponent(gridParam.modelParamA, ipf, ipg)
componentB = bm.genComponent(gridParam.modelParamB, ipf, ipg)
'''BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[restLambda, componentA, 'blue'],
						 [restLambda, componentB, 'orange']],
						[gridParam.modelParamA.teff, gridParam.modelParamB.teff], '', folder='model_gen')'''
# plt.plot(restLambda, componentA)
'''plt.show()
plt.plot(restLambda, componentB)
plt.show()'''

ipg.close()
ipf.close()

componentBR = componentB * gridParam.modelParamB.fluxRatio
# plt.plot(restLambda, componentBR)

gridParam.getRVs(visit)
componentAS = bm.shiftFlux(componentA, gridParam.modelParamA.rv)
'''plt.plot(restLambda, componentAS, color='blue')
plt.plot(restLambda, componentA, color='green')
plt.xlim(16650, 16800)
plt.show()'''
componentBS = bm.shiftFlux(componentBR, gridParam.modelParamB.rv)
BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, componentAS, 'blue', 'rest model specA' ],
						 [ restLambda, componentBS, 'orange', 'rest model specB' ]],
						[gridParam.modelParamA.teff, gridParam.modelParamB.teff], '', folder='model_gen')
'''plt.plot(restLambda, componentBS, color='blue')
plt.plot(restLambda, componentBR, color='green')
plt.xlim(16650, 16800)'''
plt.show()

binaryFlux = bm.combineFlux(componentAS, componentBS)
chi2 = calcChi2(binaryFlux, shiftedSpec, conterr) / (len(binaryFlux) - 5)
print(chi2)
BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, binaryFlux, 'blue', 'Model' ],
						 [ restLambda, shiftedSpec, 'orange', 'Data' ]],
						[gridParam.modelParamA.teff, gridParam.modelParamB.teff], '', folder='model_gen')
# plt.plot(restLambda, binaryFlux)
plt.show()
BinPlot.plotDeltaVCheck(locationID, apogeeID, visit,
						[[ restLambda, binaryFlux, 'blue', 'Model' ]],
						[gridParam.modelParamA.teff, gridParam.modelParamB.teff], '', folder='model_gen')

plt.show()
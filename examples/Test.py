# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import apogee.tools.read as apread
import apogee.spec.plot as splot
from matplotlib.pyplot import draw, show

data = apread.rcsample()
indx= data['SNR'] > 200.
data= data[indx]

splot.waveregions(data[3513]['LOCATION_ID'],data[3513]['APOGEE_ID'],ext=1,
                  labelID=data[3513]['APOGEE_ID'],
                  labelTeff=data[3513]['TEFF'],
                  labellogg=data[3513]['LOGG'],
                  labelmetals=data[3513]['METALS'],
                  labelafe=data[3513]['ALPHAFE'])
draw()
show()
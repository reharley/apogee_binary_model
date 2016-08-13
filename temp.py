
# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from apogee.tools import download
from apogee.modelspec import ferre
import matplotlib.pyplot as plt
# download.ferreModelLibrary(lib='F',pca=True,sixd=False,unf=True,dr=None,convertToBin=False)
mspecs = ferre.interpolate(3500.,2.5,-0.1,0.1,0.,0.)
plt.plot(mspecs)
plt.show()
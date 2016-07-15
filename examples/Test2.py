# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from apogee.tools import download
download.ferreModelLibrary(lib='F',pca=True,sixd=True,unf=False,dr=None,convertToBin=True)
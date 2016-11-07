# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import Grid

# The number of passes to go through the grid
passCount = 1
Grid.runGrid(passCount, filename='lists/binaries3.dat')
# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import Grid

# The number of passes to go through the grid
passCount = 10
Grid.runGrid(passCount)
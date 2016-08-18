# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import Grid
from Timer import Timer
# The number of passes to go through the grid
passCount = 10
timer = Timer()
timer.start()
Grid.runGrid(passCount)
print('Total run time: ' + str(round(timer.end(), 2)) + str('s'))
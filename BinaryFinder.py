# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from BinFinderTools import *
import apogee.tools.read as apread
from Timer import Timer

# Get all Targets
apogeeIDs, locationIDs = getAllTargets()

t = Timer()
t.start()
recordTargets(locationIDs, apogeeIDs)
print("done", t.current())
t.end()

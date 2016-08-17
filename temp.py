# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()
import threading
import time
import sys

runGrid = [None]
def childThreadTask(grid):
	if (grid[0] == None):
		grid[0] = True
	while(grid[0] == True):
		sys.stdout.write('running\n')
		time.sleep(2)
	return
def display(grid):
	while(True):
		print('hello')
		if (raw_input() == 'q'):
			grid[0] = False
			return
		else:
			print('still running')
print('hi')
t = threading.Thread(target=childThreadTask, args=(runGrid))
t.daemon = True
t.start()
t2 = threading.Thread(target=display, args=(runGrid))
t2.daemon = True
t2.start()
t.join()

print('closed')
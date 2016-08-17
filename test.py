# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

import numpy as np

apogeeIDs = np.loadtxt('lists/templist.dat', delimiter=',', usecols=[0], dtype=str, skiprows=1)
f = open('lists/temp.csv', 'w')
for apogeeID in apogeeIDs:
	baseURL = 'http://simbad.u-strasbg.fr/simbad/sim-coo?Coord=+&CooFrame=FK5&CooEpoch=2000&CooEqui=2000&CooDefinedFrames=none&Radius=2&Radius.unit=arcsec&submit=submit+query'
	temp = apogeeID
	temp = temp.replace('2M', '')
	temp = temp.replace('+', '+%2B')
	temp = temp.replace('-', '-%2B')
	try:
		temp = temp[:2] + '+' + temp[2:4] + '+' + temp[4:6] + '.' + temp[6:14] + '+' + temp[14:16] + '+' + temp[16:18] + '.' + temp[18]
	except:
		print(apogeeID, 'failed')
		f.write(apogeeID + ', \n')
		continue
	temp = temp.replace('-%2B', '-')
	
	index = baseURL.index('+&CooFrame=')
	temp = baseURL[:index] + temp + baseURL[index:]
	f.write(apogeeID + ',' + temp + '\n')
f.close()
# I forget constantly...
import sys
print(sys.version)

# This is for VS code only.
import vsEnvironSetup
vsEnvironSetup.setVariables()

from images2gif import writeGif
from PIL import Image
import os


os.chdir('model_plots')
subdirs = os.listdir('.')[1:] # disclude first directory (junk data)
print(subdirs)
i = 0

for subdir in subdirs:
	file_names = sorted((fn for fn in os.listdir(subdir) if fn.endswith('.png')))
	#['animationframa.png', 'animationframb.png', ...] "

	os.chdir(subdir)
	images = [Image.open(fn) for fn in file_names]

	size = (1920,1080)
	for im in images:
		im.thumbnail(size, Image.ANTIALIAS)

	filename = subdir + '.gif'
	writeGif(filename, images, duration=0.3)
	os.chdir('..')
	
	i+= 1
	print(str(i) + '/' + str(len(subdirs)))
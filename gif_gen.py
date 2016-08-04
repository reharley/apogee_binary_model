from images2gif import writeGif
from PIL import Image
import os

def cleanSubdirs(subdirs):
	if subdirs[0] == '.DS_Store':
		return subdirs[1:]
	return subdirs

def gifGen(folder):
	os.chdir('/Users/harleyr/Documents/plots/' + folder)
	subdirs1 = cleanSubdirs(os.listdir('.'))
	
	for subdir1 in subdirs1:
		os.chdir(subdir1)
		subdirs = cleanSubdirs(os.listdir('.'))
		i = 0
		for subdir in subdirs:
			file_names = sorted((fn for fn in cleanSubdirs(os.listdir(subdir)) if fn.endswith('.png')))
			#['animationframa.png', 'animationframb.png', ...] "

			os.chdir(subdir)
			images = [Image.open(fn) for fn in file_names]

			size = (1920,1080)
			for im in images:
				im.thumbnail(size, Image.ANTIALIAS)

			filename = subdir + '.gif'
			writeGif(filename, images, duration=0.3)
			os.chdir('../')
			
			i+= 1
			print(str(i) + '/' + str(len(subdirs)))
		os.chdir('../')
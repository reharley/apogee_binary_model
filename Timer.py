import time
class Timer:
	def __init__(self):
		self.startTime = 0.0
	
	def start(self):
		self.startTime = time.time()
	
	def end(self):
		if (self.startTime != 0.0):
			temp = time.time() - self.startTime
			self.startTime = 0.0
			return temp
		return 0.0

	def current(self):
		temp = time.time() - self.startTime
		hrs = temp/3600
		temp%= 3600
		mins = temp/60
		sec = temp %60
		return "{0}:{1}:{2}".format(hrs,mins,sec)
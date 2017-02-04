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
		return "{0}:{1}:{2}".format(temp/3600,temp/60,temp%60)
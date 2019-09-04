from threading import Thread, RLock
import time, datetime, pytz, sys

PRINT_LOCK = RLock()

"""
	defines common implementation for the threaded bot
"""
class CustomThread(Thread):
	def __init__(self, id):
		super(CustomThread, self).__init__();
		self.daemon = True
		self.id = id

	def print(self, *args):
		with PRINT_LOCK:
			print(datetime.datetime.now().time(), "| task", self.id, "|", *args)
			sys.stdout.flush()
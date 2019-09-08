## a must for py2
from __future__ import print_function

import datetime
from colorama import init
from termcolor import colored
from threading import RLock

PRINT_LOCK = RLock()

## initialize colorama
init()
_id = 1

FORMAT = "%m-%d-%Y %H:%M:%S.%f"

class Printer:
	def __init__(self):
		global _id
		self.id = str(_id)
		_id += 1

	def print(self, *args):
		with PRINT_LOCK:
			print(datetime.datetime.now().strftime(FORMAT)[:-3], " | task", self.id, "|", *args)

	def info(self, *args):
		with PRINT_LOCK:
			print(datetime.datetime.now().strftime(FORMAT)[:-3], "|", colored("[INFO]", 'green'), " | task", self.id, "|", *args)

	def error(self, *args):
		with PRINT_LOCK:
			print(datetime.datetime.now().strftime(FORMAT)[:-3], "|", colored("[ERROR]", 'red'), "| task", self.id, "|", *args)

	def warning(self, *args):
		with PRINT_LOCK:
			print(datetime.datetime.now().strftime(FORMAT)[:-3], "|", colored("[WARN]", 'yellow'), " | task", self.id, "|", *args)

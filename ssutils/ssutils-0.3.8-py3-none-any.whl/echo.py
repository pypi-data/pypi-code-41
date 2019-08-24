import datetime
import time
	
class Screenwriter:

	prefix_pattern = ''
	max_len = 1000

	def __init__(self, p_prefix_pattern='%Y-%m-%d-%H:%M:%S '):
		self.prefix_pattern = p_prefix_pattern
		self.max_len = 80

	def set_maxlen (self, len):
		self.max_len = len

	def echo (self, mesg='', add_prefix=''):
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime(self.prefix_pattern)
		finals = str(st) + add_prefix + str(mesg)
		if len(finals) > self.max_len:
			finals = finals[:self.max_len-2] + '..'
		print (finals)

	def error (self, mesg=''):
		self.echo (mesg, 'ERROR: ')

	def warn (self, mesg=''):
		self.echo (mesg, 'WARN:  ')

	def info (self, mesg=''):
		self.echo (mesg, 'INFO:  ')

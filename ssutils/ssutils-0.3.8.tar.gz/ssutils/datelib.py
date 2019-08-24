from datetime import date
from datetime import timedelta
import datetime

class Date:

	def __init__(self):
		self.today = date.today()
		
	def get_quarter (self, datein):
		sd = str(datein)
		sdin = int(sd[5:][:2])
		if sdin in (1, 2, 3):
			return 'Q1'
		elif sdin in (4, 5, 6):
			return 'Q2'
		elif sdin in (7, 8, 9):
			return 'Q3'
		elif sdin in (10, 11, 12):
			return 'Q4'
		return 'Q?'

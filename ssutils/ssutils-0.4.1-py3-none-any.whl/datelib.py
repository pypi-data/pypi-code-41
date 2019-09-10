from datetime import date
from datetime import timedelta
import datetime

class Date:

	def __init__(self):
		self.today = date.today()

	def get_quarter (self, datein=str(date.today())):
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

	def get_year_week_number (self, datein=str(date.today())):
		dt = datetime.datetime.strptime(datein, "%Y-%m-%d").date()
		wd = dt.isocalendar()[1]
		if wd == 1 and datein[5:7]== '12':
			wd = 53
		return (datein[:4] + '/' + str(wd).rjust(2).replace(' ','0'))

	def get_week_number (self, datein=str(date.today())):
		dt = datetime.datetime.strptime(datein, "%Y-%m-%d").date()
		wd = dt.isocalendar()[1]
		return int(wd)

	def get_month (self, datein=str(date.today())):
		sd = str(datein)
		sdin = int(sd[5:][:2])
		if sdin == 1:
			return 'January'
		elif sdin == 2:
			return 'February'
		elif sdin == 3:
			return 'March'
		elif sdin == 4:
			return 'April'
		elif sdin == 5:
			return 'May'
		elif sdin == 6:
			return 'June'
		elif sdin == 7:
			return 'July'
		elif sdin == 8:
			return 'August'
		elif sdin == 9:
			return 'September'
		elif sdin == 10:
			return 'October'
		elif sdin == 11:
			return 'November'
		elif sdin == 12:
			return 'December'
		return datein

	def get_mon (self, datein=str(date.today())):
		return (self.get_month(datein)[:3])

	def get_year_start (self, datein=str(date.today())):
		return str(datein)[:4] + '-01-01'

	def get_year_end (self, datein=str(date.today())):
		return str(datein)[:4] + '-12-31'

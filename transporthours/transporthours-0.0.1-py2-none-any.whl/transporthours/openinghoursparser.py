# -*- coding: utf-8 -*-

import re

class OpeningHoursParser:
	"""
	OpeningHoursParser handles parsing of opening_hours=* tag.
	It only supports basic version of the tag, as we don't need full implementation for public transport hours.
	"""
	def __init__(self, value):
		"""
		Creates the OpeningHoursParser Object with OSM opening_hours string
		# param value (string): The opening_hours=* value
		"""
		self.openingHours = {}
		self._parse(value)

		# Check if opening hours is empty (invalid parsing)
		if len([ k for k in self.openingHours if len(k) == 0 ]) == len(self.openingHours):
			raise Exception("Can't parse opening_hours : "+value)

	def getTable(self):
		"""
		Get the parsed value as a table
		# return (dict): The hours, as { day: [ hours ] }
		"""
		return self.openingHours

	def _parse(self, inp):
		"""
		Parses the input and creates openingHours Object
		"""
		self._initOpeningHoursObj()
		inp = self._simplify(inp)
		parts = self._splitHard(inp)

		for part in parts:
			self._parseHardPart(part)

	def _simplify(self, txt):
		if txt == "24/7":
			txt = "mo-su 00:00-24:00; ph 00:00-24:00"
		txt = txt.lower()
		txt = txt.strip()

		txt = re.sub(" +(?= )", "", txt)

		txt = txt.replace(' -', '-')
		txt = txt.replace('- ', '-')

		txt = txt.replace(' :', ':')
		txt = txt.replace(': ', ':')

		txt = txt.replace(' ,', ',')
		txt = txt.replace(', ', ',')

		txt = txt.replace(' ;', ';')
		txt = txt.replace('; ', ';')
		return txt

	def _splitHard(self, inp):
		return inp.split(';')

	def _parseHardPart(self, part):
		if part == "24/7":
			part = "mo-su 00:00-24:00"

		segments = re.compile("\ |\,").split(part)

		tempData = {}
		days = []
		times = []
		isValid = False

		for i in range(len(segments)):
			segment = segments[i]
			if self._checkDay(segment):
				isValid = True
				if len(times) == 0:
					days = days + self._parseDays(segment)
				else:
					# append
					for day in days:
						if tempData[day]:
							tempData[day] = tempData[day] + times
						else:
							tempData[day] = times
					days = self._parseDays(segment)
					times = []
			if self._checkTime(segment):
				isValid = True
				if i == 0 and len(days) == 0:
					days = self._parseDays("Mo-Su,PH")
				if segment == "off":
					times = "off"
				else:
					times.append(self._cleanTime(segment))

		# Raise exception if no read part is valid
		if not isValid:
			raise Exception("Can't parse opening_hours : "+part)

		# commit last times to it days
		for day in days:
			if day in tempData:
				tempData[day] = tempData[day] + times
			else:
				tempData[day] = times

		for day in days:
			if times == "off":
				tempData[day] = []
			elif len(times) == 0:
				tempData[day] = ["00:00-24:00"]

		# apply data to main obj
		for key in tempData:
			self.openingHours[key] = tempData[key]

	def _parseDays(self, part):
		part = part.lower()
		days = []
		softparts = part.split(',')
		for part in softparts:
			rangecount = len(re.findall("\-", part))
			if rangecount == 0:
				days.append(part)
			else:
				days = days + self._calcDayRange(part)

		return days

	def _cleanTime(self, time):
		if re.match("^[0-9]:[0-9]{2}", time):
			time = "0"+time
		if re.match("^[0-9]{2}:[0-9]{2}\-[0-9]:[0-9]{2}", time):
			time = time[0:6]+"0"+time[6:]
		return time

	def _initOpeningHoursObj(self):
		self.openingHours = {
			"su": [],
			"mo": [],
			"tu": [],
			"we": [],
			"th": [],
			"fr": [],
			"sa": [],
			"ph": []
		}

	def _calcDayRange(self, daysRange):
		"""
		Calculates the days in range "mo-we" -> ["mo", "tu", "we"]
		"""
		defDays = {
			"su": 0,
			"mo": 1,
			"tu": 2,
			"we": 3,
			"th": 4,
			"fr": 5,
			"sa": 6
		}

		rangeElements = daysRange.split('-')

		dayStart = defDays[rangeElements[0]]
		dayEnd = defDays[rangeElements[1]]

		numberRange = self._calcRange(dayStart, dayEnd, 6)
		outRange = []

		for n in numberRange:
			for key in defDays:
				if defDays[key] == n:
					outRange.append(key)

		return outRange

	def _calcRange(self, minv, maxv, maxval):
		"""
		Creates a range between two number.
		if the max value is 6 a range bewteen 6 and 2 is 6, 0, 1, 2
		"""
		if minv == maxv:
			return [minv]
		myRange = [minv]
		rangepoint = minv
		while rangepoint < (maxv if (minv < maxv) else maxval):
			rangepoint += 1
			myRange.append(rangepoint)
		if minv > maxv:
			# add from first in list to max value
			myRange = myRange + self._calcRange(0, maxv, maxval)

		return myRange

	def _checkTime(self, inp):
		"""
		Check if string is time range
		"""
		# e.g. 09:00+
		if re.search("[0-9]{1,2}:[0-9]{2}\+", inp):
			return True
		# e.g. 08:00-12:00
		if re.search("[0-9]{1,2}:[0-9]{2}\-[0-9]{1,2}:[0-9]{2}", inp):
			return True
		# off
		if re.search("off", inp):
			return True
		return False

	def _checkDay(self, inp):
		"""
		check if string is day or dayrange
		"""
		days = ["mo", "tu", "we", "th", "fr", "sa", "su", "ph"]
		if re.search("\-", inp):
			rangelements = inp.split('-')
			if rangelements[0] in days and rangelements[1] in days:
				return True
		else:
			if inp in days:
				return True
		return False

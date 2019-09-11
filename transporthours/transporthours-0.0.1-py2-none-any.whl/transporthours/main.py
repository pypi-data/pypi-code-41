# -*- coding: utf-8 -*-

import re
import functools
from .openinghoursparser import OpeningHoursParser

TAG_UNSET = "unset"
TAG_INVALID = "invalid"
DAYS_ID = [ "mo", "tu", "we", "th", "fr", "sa", "su", "ph" ]

class Main:
	"""
	Main class of the library.
	It contains all main functions which can help managing public transport hours.
	"""

	def tagsToGtfs(self, tags):
		"""
		Convert OpenStreetMap tags into a GTFS-like format (list of dict having format { eachWeekDay: True/False, start_time: string, end_time: string, headway: int }.
		Parsed tags are : interval=\*, opening_hours=\* and interval:conditional=\*

		# param tags (dict): OpenStreetMap tags
		# return dict[]: list of dictionaries, each one representing a line of GTFS hours CSV file
		"""
		hours = self.tagsToHoursObject(tags)

		if hours['allComputedIntervals'] == TAG_INVALID:
			raise Exception("OSM tags describing route hours are probably invalid, and can't be read")
		elif hours['allComputedIntervals'] == TAG_UNSET:
			return []
		else:
			result = []

			daysId = [ "mo", "tu", "we", "th", "fr", "sa", "su", "ph" ]

			# Read each period(days, intervals)
			for period in sorted(hours['allComputedIntervals'], key=lambda x: daysId.index(x['days'][0])):
				periodGtfs = {}

				# Interpret days (we ignore ph as not used by GTFS)
				days = [ d for d in period['days'] if d != "ph" ]
				if len(days) > 0:
					periodGtfs['monday'] = "mo" in days
					periodGtfs['tuesday'] = "tu" in days
					periodGtfs['wednesday'] = "we" in days
					periodGtfs['thursday'] = "th" in days
					periodGtfs['friday'] = "fr" in days
					periodGtfs['saturday'] = "sa" in days
					periodGtfs['sunday'] = "su" in days

					# Interpret intervals
					for hourRange in sorted(period['intervals'].keys()):
						periodHourGtfs = dict(periodGtfs)
						periodHourGtfs['start_time'] = hourRange.split("-")[0] + ":00"
						periodHourGtfs['end_time'] = hourRange.split("-")[1] + ":00"
						periodHourGtfs['headway'] = period['intervals'][hourRange] * 60

						# Add to result
						result.append(periodHourGtfs)

			return result

	def tagsToHoursObject(self, tags):
		"""
		Converts OpenStreetMap tags into a ready-to-use object representing the hours of the public transport line.
		Parsed tags are : interval=\*, opening_hours=\* and interval:conditional=\*

		# param tags (dict): The list of tags from OpenStreetMap
		# return dict: The hours of the line, with structure { opens: object in format given by #OpeningHoursParser.gettable(), defaultInterval: minutes (int), otherIntervals: interval rules object, otherIntervalsByDays: list of interval by days (structure: { days: string[], intervals: { hoursRange: interval } }), allComputedIntervals: same as otherIntervalsByDays but taking also default interval and opening_hours }. Each field can also have value "unset" if no tag is defined, or "invalid" if tag can't be read.
		"""

		# Read opening_hours
		opens = TAG_UNSET
		try:
			opens = OpeningHoursParser(tags['opening_hours']).getTable() if 'opening_hours' in tags else TAG_UNSET
		except:
			opens = TAG_INVALID

		# Read interval
		interval = TAG_UNSET
		try:
			interval = self.intervalStringToMinutes(tags['interval']) if 'interval' in tags else TAG_UNSET
		except:
			interval = TAG_INVALID

		# Read interval:conditional
		intervalCond = TAG_UNSET
		intervalCondByDay = TAG_UNSET
		try:
			intervalCond = self.intervalConditionalStringToObject(tags["interval:conditional"]) if "interval:conditional" in tags else TAG_UNSET
			intervalCondByDay = self._intervalConditionObjectToIntervalByDays(intervalCond) if intervalCond != TAG_UNSET else TAG_UNSET
		except:
			intervalCond = TAG_INVALID
			intervalCondByDay = TAG_INVALID

		# Create computed calendar of intervals using previous data
		computedIntervals = TAG_UNSET
		try:
			computedIntervals = self._computeAllIntervals(opens, interval, intervalCondByDay)
		except:
			computedIntervals = TAG_INVALID

		# Send result
		return {
			"opens": opens,
			"defaultInterval": interval,
			"otherIntervals": intervalCond,
			"otherIntervalsByDays": intervalCondByDay,
			"allComputedIntervals": computedIntervals
		}

	def intervalConditionalStringToObject(self, intervalConditional):
		"""
		Reads an interval:conditional=* tag from OpenStreetMap, and converts it into a dict.

		# param intervalConditional (string): The {@link https://wiki.openstreetmap.org/wiki/Key:interval|interval:conditional} tag
		# return (dict[]): A list of rules, each having structure { interval: minutes (int), applies: {@link #gettable|opening hours table} }
		"""
		return [ self._readSingleIntervalConditionalString(p) for p in self._splitMultipleIntervalConditionalString(intervalConditional) ]

	def _splitMultipleIntervalConditionalString(self, intervalConditional):
		"""
		Splits several conditional interval rules being separated by semicolon.

		# param intervalConditional (string)
		# return (string[]): List of single rules
		"""
		if "(" in intervalConditional:
			semicolons = [i for i, ltr in enumerate(intervalConditional) if ltr == ";"]
			cursor = 0
			stack = []

			while len(semicolons) > 0:
				scid = semicolons[0]
				part = intervalConditional[cursor:scid]

				if re.search("^[^\(\)]+$", part) or re.search("\(.*\)", part):
					stack.append(part)
					cursor = scid+1

				semicolons.pop(0)

			stack.append(intervalConditional[cursor:])
			return [ p.strip() for p in stack if len(p.strip()) > 0 ]
		else:
			return [ p.strip() for p in intervalConditional.split(";") if len(p.strip()) > 0 ]

	def _readSingleIntervalConditionalString(self, intervalConditional):
		"""
		Parses a single conditional interval value (for example : `15 @ (08:00-15:00)`).
		This should be used as many times as you have different rules (separated by semicolon).

		# param intervalConditional (string)
		# return (dict): dictionary with structure { interval: minutes (int), applies: OpeningHoursParser.gettable() structure} }
		"""
		result = {}
		parts = [ p.strip() for p in intervalConditional.split("@") ]

		if len(parts) != 2:
			raise Exception("Conditional interval can't be parsed : "+intervalConditional)

		# Read interval
		result['interval'] = self.intervalStringToMinutes(parts[0])

		# Read opening hours
		if re.search("^\(.*\)$", parts[1]):
			parts[1] = parts[1][1:len(parts[1])-1]

		result['applies'] = OpeningHoursParser(parts[1]).getTable()

		return result

	def _intervalConditionObjectToIntervalByDays(self, intervalConditionalObject):
		"""
		Transforms an object containing the conditional intervals into an object structured day by day.
		"""
		result = []
		itvByDay = {}

		# List hours -> interval day by day
		for itv in intervalConditionalObject:
			for day, hours in itv['applies'].items():
				if day not in itvByDay:
					itvByDay[day] = {}
				for h in hours:
					itvByDay[day][h] = itv['interval']

		# Merge days
		for day, intervals in itvByDay.items():
			if len(intervals) > 0:
				# Look for identical days
				ident = [ r for r in result if r['intervals'] == intervals ]

				if len(ident) == 1:
					ident[0]['days'].append(day)
				else:
					result.append({ "days": [ day ], "intervals": intervals })

		# Sort by days
		for itv in result:
			itv['days'].sort(key = lambda x: DAYS_ID.index(x))

		result.sort(key = lambda x: DAYS_ID.index(x['days'][0]))

		return result

	def _flatList(self, myList):
		flatList=[]
		for eachList in myList:
			for eachItem in eachList:
				flatList.append(eachItem)
		return flatList

	def _computeAllIntervals(self, openingHours, interval, intervalCondByDay):
		"""
		Reads all information, and generates a merged calendar of all intervals.
		"""

		# If opening hours or interval is invalid, returns interval conditional as is
		if openingHours == TAG_INVALID or interval == TAG_INVALID or interval == TAG_UNSET or intervalCondByDay == TAG_INVALID:
			return TAG_INVALID if (openingHours == TAG_INVALID or interval == TAG_INVALID) and intervalCondByDay == TAG_UNSET else intervalCondByDay
		else:
			myIntervalCondByDay = [] if intervalCondByDay == TAG_UNSET else intervalCondByDay

			# Check opening hours, if missing we default to 24/7
			myOH = openingHours
			if openingHours == TAG_UNSET:
				myOH = OpeningHoursParser("24/7").getTable()

			# Copy existing intervals (split day by day)
			result = []
			for di in myIntervalCondByDay:
				for d in di['days']:
					result.append({ "days": [d], "intervals": di['intervals'] })

			# Complete existing days
			result = list(result)
			for di in result:
				di['intervals'] = self._mergeIntervalsSingleDay(myOH[di['days'][0]], interval, di['intervals'])

			# List days not in myIntervalCondByDay, and add directly opening hours
			# Was: daysInCondInt = [...new Set(myIntervalCondByDay.map(d => d.days).flat())]
			daysInCondInt = list(set(self._flatList([ d['days'] for d in myIntervalCondByDay ])))
			missingDays = [ d for d in myOH if d not in daysInCondInt ]
			missingDaysOH = {}
			for day in missingDays:
				missingDaysOH[day] = myOH[day]

			result = result + self._intervalConditionObjectToIntervalByDays([{ "interval": interval, "applies": missingDaysOH }])

			# Merge similar days
			i = 1
			while i < len(result):
				j = 0
				while j < i:
					if result[i]['intervals'] == result[j]['intervals']:
						result[j]['days'] = result[j]['days'] + result[i]['days']
						del result[i]
						i -= 1
						break
					j += 1
				i += 1

			# Sort results by day
			for r in result:
				r['days'].sort(key=lambda x: DAYS_ID.index(x))

			result.sort(key=lambda x: DAYS_ID.index(x['days'][0]))

			return result

	def _hourRangeWithin(self, wider, smaller):
		"""
		Check if an hour range is contained in another one
		"""
		if wider == smaller:
			return True
		else:
			# During day
			if wider[0] <= wider[1]:
				if smaller[0] > smaller[1]:
					return False
				else:
					return wider[0] <= smaller[0] and smaller[0] < wider[1] and wider[0] < smaller[1] and smaller[1] <= wider[1]
			# Over midnight
			else:
				# Either before or after midnight
				if smaller[0] <= smaller[1]:
					# All after wider start
					if wider[0] <= smaller[0] and wider[0] <= smaller[1]:
						return True
					else:
						return False
				# Over midnight
				else:
					return wider[0] <= smaller[0] and smaller[0] <= "24:00" and "00:00" <= smaller[1] and smaller[1] <= wider[1]

	def _hourRangeOverlap(self, first_range, second_range):
		"""
		Check if an hour range overlap another one
		"""
		if first_range == second_range:
			return False
		else:
			if not first_range[0] <= second_range[0]:
				_ = first_range
				first_range = second_range
				second_range = _

			# First one is during day
			if first_range[0] <= first_range[1]:
				return second_range[0] < first_range[1]

			# First one is over midnight
			else:
				# Second one is during day (Either before or after midnight)
				if second_range[0] <= second_range[1]:
					if first_range[0] <= second_range[0] and first_range[0] <= second_range[1]:
						return True
					else:
						return False
				# Second one is over midnight
				else:
					return True

	def _mergeIntervalsSingleDay(self, hours, interval, condIntervals):
		"""
		Add default interval within opening hours to conditional intervals
		"""
		hourRangeToArr = lambda hr: [ h.split("-") for h in hr ]
		ohHours = hourRangeToArr(hours)
		condHours = hourRangeToArr(condIntervals)

		# Check all conditional hours belong into opening hours
		for condHours_elem in condHours:
				if not any([ohh for ohh in ohHours if self._hourRangeWithin(ohh, condHours_elem) ]):
						raise Exception("Conditional intervals are not contained in opening hours")

		# Check conditional hours are not overlapping
		goneOverMidnight = False
		condHours.sort(key = lambda x: self.intervalStringToMinutes(x[0]))

		for i in range(len(condHours)):
			ch = condHours[i]
			if not goneOverMidnight:
				if ch[0] > ch[1]:
					goneOverMidnight = True

				for j in range(i):
					if self._hourRangeOverlap(ch, condHours[j]):
						raise Exception("Conditional intervals are not exclusive (they overlaps)")
			else:
				raise Exception("Conditional intervals are not exclusive (several intervals after midnight)")

		ohHoursWithoutConds = []

		for ohh in ohHours:
			holes = []
			thisCondHours = [ ch for ch in condHours if self._hourRangeWithin(ohh, ch) ]

			for i in range(len(thisCondHours)):
				ch = thisCondHours[i]
				isFirst = i == 0
				isLast = i == len(thisCondHours) - 1

				if isFirst and ohh[0] < ch[0]:
					holes.append(ohh[0])
					holes.append(ch[0])

				if not isFirst and thisCondHours[i-1][1] < ch[0]:
					holes.append(thisCondHours[i-1][1])
					holes.append(ch[0])

				if isLast:
					appendLast = False

					# opening hours before midnight
					if ohh[0] < ohh[1]:
						if ch[1] < ohh[1]:
							appendLast = True
					# opening hours going after midnight
					else:
						# current range before midnight
						if ch[0] < ch[1]:
							appendLast = True
						# current range going through midnight
						else:
							# Current range ending before opening hour end
							if ch[1] < ohh[1]:
								appendLast = True

					if appendLast:
						holes.append(ch[1])
						holes.append(ohh[1])

			ohHoursWithoutConds += [ holes[i-1]+"-"+holes[i] for i in range(len(holes)) if i % 2 == 1 ]

		result = {}
		for h in ohHoursWithoutConds:
			result[h] = interval

		result.update(condIntervals)

		return result

	def intervalStringToMinutes(self, interval):
		"""
		Converts an interval=* string into an amount of minutes

		>>> intervalStringToMinutes("00:10")
		10
		"""
		interval = interval.strip()

		# hh:mm:ss
		if re.search("^\d{1,2}:\d{2}:\d{2}$", interval):
			parts = [ int(t) for t in interval.split(":") ]
			return parts[0] * 60 + parts[1] + parts[2] / 60.0

		# hh:mm
		elif re.search("^\d{1,2}:\d{2}$", interval):
			parts = [ int(t) for t in interval.split(":") ]
			return parts[0] * 60 + parts[1]

		# mm
		elif re.search("^\d+$", interval):
			return int(interval)

		# invalid
		else:
			raise Exception("Interval value can't be parsed : "+interval)

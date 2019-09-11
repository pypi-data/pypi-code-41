# -*- coding: utf-8 -*-

from transporthours.openinghoursparser import OpeningHoursParser
import unittest

class OpeningHoursParserTest(unittest.TestCase):
	#
	# Constructor
	#
	def test_constructor_handles_hours(self):
		value = "10:00-12:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": ["10:00-12:00"],
			"we": ["10:00-12:00"],
			"th": ["10:00-12:00"],
			"fr": ["10:00-12:00"],
			"sa": ["10:00-12:00"],
			"su": ["10:00-12:00"],
			"ph": ["10:00-12:00"]
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_ph_off(self):
		value = "10:00-12:00; PH off";
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": ["10:00-12:00"],
			"we": ["10:00-12:00"],
			"th": ["10:00-12:00"],
			"fr": ["10:00-12:00"],
			"sa": ["10:00-12:00"],
			"su": ["10:00-12:00"],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_full_week_ph(self):
		value = "Mo-Su,PH 10:00-12:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": ["10:00-12:00"],
			"we": ["10:00-12:00"],
			"th": ["10:00-12:00"],
			"fr": ["10:00-12:00"],
			"sa": ["10:00-12:00"],
			"su": ["10:00-12:00"],
			"ph": ["10:00-12:00"]
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_day_hours(self):
		value = "Mo 10:00-12:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": [],
			"we": [],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_day_hours_short(self):
		value = "Mo 1:00-5:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["01:00-05:00"],
			"tu": [],
			"we": [],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_days_ranges_hours(self):
		value = "Mo-We 10:00-12:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": ["10:00-12:00"],
			"we": ["10:00-12:00"],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_days_list_hours(self):
		value = "Mo,We 10:00-12:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": [],
			"we": ["10:00-12:00"],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_days_different_hours(self):
		value = "Mo-We 10:00-12:00; Th-Sa 09:00-15:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00"],
			"tu": ["10:00-12:00"],
			"we": ["10:00-12:00"],
			"th": ["09:00-15:00"],
			"fr": ["09:00-15:00"],
			"sa": ["09:00-15:00"],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_hours_ranges_same_day(self):
		value = "Mo-We 10:00-12:00, 17:00-19:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["10:00-12:00", "17:00-19:00"],
			"tu": ["10:00-12:00", "17:00-19:00"],
			"we": ["10:00-12:00", "17:00-19:00"],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_days_only(self):
		value = "Mo-We"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["00:00-24:00"],
			"tu": ["00:00-24:00"],
			"we": ["00:00-24:00"],
			"th": [],
			"fr": [],
			"sa": [],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_days_only_subpart(self):
		value = "Mo-We; Sa 01:00-15:00"
		oh = OpeningHoursParser(value)
		result = oh.getTable()
		expected = {
			"mo": ["00:00-24:00"],
			"tu": ["00:00-24:00"],
			"we": ["00:00-24:00"],
			"th": [],
			"fr": [],
			"sa": ["01:00-15:00"],
			"su": [],
			"ph": []
		}
		self.assertEqual(result, expected)

	def test_constructor_handles_invalid(self):
		value = "This is not opening_hours !"
		self.assertRaises(Exception, OpeningHoursParser, value)

if __name__ == '__main__':
	unittest.main()

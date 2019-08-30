# !/usr/bin/python3
# -*- coding: utf-8 -*-

class MCVBase(object):
	"""
	Abstract class of a filter.  
	The filters classes should reemplement the methods
	present on this class.
	"""


	def __init__(self, **kwargs):
		self.load(kwargs)

	def load(self, data, **kwargs):
		pass

	def save(self, data, **kwargs):
		return data

	def process(self, input_data, **kwargs):
		"""Filter implmentation."""
		return input_data

	def processflow(self, input_data, **kwargs):
		"""Process all the filters from the hierarchy."""
		return input_data

	def end(self, input_data, **kwargs):
		return input_data

	def clear(self): 
		"""
		Method used to reset current filter data.
		Used to re-start an analysis from scratch.
		"""
		pass
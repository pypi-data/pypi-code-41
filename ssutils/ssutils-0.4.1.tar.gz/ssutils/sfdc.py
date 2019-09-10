import sys
import os
import datetime
import time
import inspect
from ssutils.echo import Screenwriter
from simple_salesforce import Salesforce

class Sfdc:

	def __init__(self, u, p, t, verbose=True):
		self.sf                    = None
		self.sw                    = Screenwriter ()
		self.object_labels         = {}
		self.object_desc           = {}
		self.fx_rates              = {}
		self.table_data            = {}
		self.conected              = False
		self.standard_object_names = set()
		self.custom_object_names   = set()
		self.custom_setting_names  = set()
		self.userid      = u
		self.password    = p
		self.token       = t
		self.verboseMode = verbose
		
	def connect (self):
		if self.verboseMode:
			self.sw.echo ("Connecting to SFDC with Userid [" + self.userid + "]")
		self.sf = Salesforce(username=self.userid, password=self.password, security_token=self.token)
		if self.verboseMode:
			self.sw.echo ("Connected")
	
	def load_metadata (self):
		if len(self.object_labels.keys()) == 0:
			if self.verboseMode:
				self.sw.echo ("Scanning Standard & Custom Objects")
			for x in self.sf.describe()["sobjects"]:
				api_name = x["name"]
				label = x["label"]
				isCustomSetting = x["customSetting"]
				isCustomObject = x["custom"]
				self.object_labels[api_name] = label
				if isCustomSetting:
					self.custom_setting_names.add (api_name)
				elif isCustomObject:
					self.custom_object_names.add (api_name)
				else:
					self.standard_object_names.add (api_name)

	def describe_object (self, api_name):
		if api_name not in self.object_desc.keys():
			if self.verboseMode:
				self.sw.echo ("Loading Metadata for [" + api_name + "]")
			resp = getattr(self.sf, api_name).describe()
			self.object_desc[api_name] = resp['fields']
		return self.object_desc[api_name]

	def load_fx_rates (self):
		if self.verboseMode:
			self.sw.echo ("Loading Currency Rates..")
		qs = "SELECT ISOCode, ConversionRate FROM CurrencyType WHERE IsActive=TRUE"
		resp = self.sf.query_all (qs)
		loopIndex = 0
		while loopIndex < len(resp['records']):
			self.fx_rates [resp['records'][loopIndex]['IsoCode']] = resp['records'][loopIndex]['ConversionRate']
			loopIndex += 1
		if self.verboseMode:
			self.sw.echo (str(len(self.fx_rates.keys())) + " Currency Rates Loaded")

	def get_amount_in_USD (self, amount, curreny_code):
		if curreny_code in self.fx_rates.keys():
			return (amount / self.fx_rates[curreny_code])

	def split_list_into_array_of_lists (self, inlist, arraysize=500):
		array_of_lists = []
		list_items = []
		for member in inlist:
			if len(list_items) >= arraysize:
				array_of_lists.append (list_items)
				list_items = list()
				list_items.append (member)
			else:
				list_items.append (member)
		if len(list_items) > 0:
			array_of_lists.append (list_items)
		return array_of_lists;

	def load_data (self, objectName, colnames, filters, joincondition=[]):
		if self.verboseMode:
			self.sw.echo ("Selecting from " + objectName + "..")
		self.table_data[objectName] = []
		query_list = []
		qs = 'SELECT '
		qs += ','.join (colnames)
		qs += ' FROM ' + objectName
		if (len(filters) > 0):
			qs += ' WHERE ' 
			qs += ' AND '.join (filters)
		if len(joincondition) == 3:
			joinField = joincondition[0]
			joinedObject = joincondition[1]
			joinedObjectCol = joincondition[2]
			joinVals = []
			for rec in self.table_data[joinedObject]:
				joinVals.append ("'" + rec[joinedObjectCol] + "'")
				if len(joinVals) >= 500:
					qsj = qs + ' AND ' + joinField + ' IN (' + ",".join(joinVals) + ")"
					query_list.append (qsj)
					joinVals = []
			if len(joinVals) > 0:
				qsj = qs + ' AND ' + joinField + ' IN (' + ",".join(joinVals) + ")"
				query_list.append (qsj)
		else:
			query_list.append (qs)

		for qs in query_list:
			resp = self.sf.query_all(qs)
			arrLen = len(resp['records'])
			loopIndex = 0
			while loopIndex < arrLen:
				rec = {}
				for col in colnames:
					if '.' in col:
						colparts = col.split ('.')
						if len(colparts) == 2:
							rec[col] = resp['records'][loopIndex][colparts[0]][colparts[1]]
					else:
						rec[col] = resp['records'][loopIndex][col]
				loopIndex += 1
				self.table_data[objectName].append (rec)
			if self.verboseMode:
				self.sw.echo (str(len(self.table_data[objectName])) + " rows Selected from " + objectName)

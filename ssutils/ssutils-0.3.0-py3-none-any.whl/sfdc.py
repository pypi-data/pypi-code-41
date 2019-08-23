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

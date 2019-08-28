#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import sys
import copy
# Local import
from . import debug


def append_to_list(list_out, elem):
	if type(elem) == str:
		if elem not in list_out:
			list_out.append(elem)
	else:
		# mulyiple imput in the list ...
		for element in elem:
			if element not in list_out:
				list_out.append(element)



class HeritageList:
	def __init__(self, heritage = None):
		self.flags = {}
		self.path = {}
		self.list_heritage = []
		if heritage != None:
			self.add_heritage(heritage)
	
	def add_heritage(self, heritage):
		if    type(heritage) == type(None) \
		   or heritage.name == "":
			return
		for element in self.list_heritage:
			if element.name == heritage.name:
				return
		self.list_heritage.append(heritage)
		self.regenerate_tree()
	
	def add_heritage_list(self, heritage_list):
		if type(heritage_list) == type(None):
			return
		for herit in heritage_list.list_heritage:
			find = False
			for element in self.list_heritage:
				if element.name == herit.name:
					find = True
			if find == False:
				self.list_heritage.append(herit)
		self.regenerate_tree()
	
	def regenerate_tree(self):
		self.flags = {}
		self.path = {}
		# reorder heritage list :
		listHeritage = self.list_heritage
		self.list_heritage = []
		# first step : add all lib with no dependency:
		for herit in listHeritage:
			if len(herit.depends) == 0:
				self.list_heritage.append(herit)
				listHeritage.remove(herit)
		while len(listHeritage) > 0:
			currentHeritageSize = len(listHeritage)
			debug.verbose("list heritage = " + str([[x.name, x.depends] for x in listHeritage]))
			# Add element only when all dependence are resolved
			for herit in listHeritage:
				listDependsName = [y.name for y in self.list_heritage]
				if all(x in listDependsName for x in herit.depends) == True:
					listHeritage.remove(herit)
					self.list_heritage.append(herit)
			if currentHeritageSize == len(listHeritage):
				debug.warning("Not resolve dependency between the library ==> can be a cyclic dependency !!!")
				for herit in listHeritage:
					self.list_heritage.append(herit)
				listHeritage = []
				debug.warning("new heritage list:")
				for element in self.list_heritage:
					debug.warning("	" + element.name + " " + str(element.depends))
		debug.verbose("new heritage list:")
		for element in self.list_heritage:
			debug.verbose("	" + element.name + " " + str(element.depends))
		for element in reversed(self.list_heritage):
			for ppp in element.path:
				value = element.path[ppp]
				if ppp not in self.path:
					self.path[ppp] = value
				else:
					append_to_list(self.path[ppp], value)
	
	def __repr__(self):
		return "{doxy:HeritageList:" + str(self.list_heritage) + "}"

class heritage:
	def __init__(self, module, target):
		self.name = ""
		self.depends = []
		## Remove all variable to prevent error of multiple definition
		self.path = {}
		self.include = ""
		# update is set at true when data are newly created ==> force upper element to update
		self.hasBeenUpdated=False
		
		if type(module) != type(None):
			# all the parameter that the upper classe need when build
			self.name = module.name
			self.depends = copy.deepcopy(module.depends)
	
	def add_depends(self, elements):
		self.depends.append(elements)
	
	def need_update(self, list):
		self.hasBeenUpdated=True
	
	def add_sub(self, other):
		if type(other) == type(None):
			debug.verbose("input of the heriatege class is None !!!")
			return
		if other.hasBeenUpdated == True:
			self.hasBeenUpdated = True
	
	def __repr__(self):
		return "{doxy:Heritage:" + str(self.name) + " ... }"



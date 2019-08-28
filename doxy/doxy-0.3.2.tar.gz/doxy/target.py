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
import os
import inspect
import fnmatch
import datetime
# Local import
from . import debug
from . import heritage
from . import tools
from . import module
from . import multiprocess
from . import env

class Target:
	def __init__(self, config):
		self.config = config
		debug.info("=================================");
		debug.info("== Target                      ==");
		debug.info("=================================");
		self.path_out = "out/doc/" + self.config["mode"] + "/"
		self.module_list = []
		self.build_done = []
	
	def __repr__(self):
		return "{doxy.Target}"
	##
	## @brief Get the fianal path ==> contain all the generated packages
	## @return The path of the pa
	##
	def get_final_path(self):
		return os.path.join(tools.get_run_path(), self.path_out)
	
	def is_module_build(self, my_module):
		for mod in self.build_done:
			if mod == my_module:
				return True
		self.build_done.append(my_module)
		return False
	
	def add_module(self, newModule):
		debug.debug("Add nodule for Taget : " + newModule.name)
		self.module_list.append(newModule)
	
	def get_module(self, name):
		for mod in self.module_list:
			if mod.name == name:
				return mod
		debug.error("the module '" + str(name) + "'does not exist/already build")
		return None
	
	def clean(self, name):
		for mod in self.module_list:
			if mod.name == name:
				mod.clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	def load_if_needed(self, name):
		for elem in self.module_list:
			if elem.name == name:
				return True
		# try to find in the local Modules:
		exist = module.exist(self, name)
		if exist == True:
			module.load_module(self, name)
			return True;
		# we did not find the module ...
		return False;
	
	def load_all(self):
		listOfAllTheModule = module.list_all_module()
		for modName in listOfAllTheModule:
			self.load_if_needed(modName)
	
	def project_add_module(self, name, projectMng, addedModule):
		for mod in self.module_list:
			if mod.name == name:
				mod.ext_project_add_module(self, projectMng, addedModule)
				return
	
	def build(self, name, packagesName=None, actions=[]):
		if    len(name.split("?")) != 1\
		   or len(name.split("@")) != 1:
			debug.error("need update")
		if actions == "":
			actions = ["build"]
		if actions == []:
			actions = ["build"]
		if type(actions) == str:
			actions = [actions]
		if name == "dump":
			debug.info("dump all")
			self.load_all()
			for mod in self.module_list:
				mod.display()
			return
		if name == "all":
			debug.info("build all")
			self.load_all()
			for mod in self.module_list:
				mod.build(self, None)
		elif name == "clean":
			debug.info("clean all")
			self.load_all()
			for mod in self.module_list:
				mod.clean(self)
		else:
			module_name = name
			action_list = actions
			debug.verbose("plop: " + str(action_list))
			for action_name in action_list:
				debug.verbose("requested : " + module_name + "?" + action_name + " [START]")
				ret = None;
				present = self.load_if_needed(module_name)
				if present == False:
					ret = [heritage.HeritageList(), False]
				else:
					for mod in self.module_list:
						if mod.name == module_name:
							if action_name[:4] == "dump":
								debug.info("dump module '" + module_name + "'")
								if len(action_name) > 4:
									debug.warning("action 'dump' does not support options ... : '" + action_name + "'")
								ret = mod.display()
								break
							elif action_name[:5] == "clean":
								debug.info("clean module '" + module_name + "'")
								if len(action_name) > 5:
									debug.warning("action 'clean' does not support options ... : '" + action_name + "'")
								ret = mod.clean(self)
								break
							elif action_name[:5] == "build":
								if len(action_name) > 5:
									debug.warning("action 'build' does not support options ... : '" + action_name + "'")
								debug.debug("build module '" + module_name + "'")
								ret = mod.build(self, None)
								break
					if ret == None:
						ret = [heritage.HeritageList(), False]
						break
					if ret == None:
						debug.error("not know module name : '" + module_name + "' to '" + action_name + "' it")
				debug.verbose("requested : " + module_name + "?" + action_name + " [STOP]")
			if len(action_list) == 1:
				return ret
	
	##
	## @brief convert a s list of string in a string separated by a ","
	## @param[in] list List of element to transform
	## @return The requested string
	##
	def generate_list_separate_coma(self, list):
		result = ""
		fistTime = True
		for elem in list:
			if fistTime == True:
				fistTime = False
			else:
				result += ","
			result += elem
		return result


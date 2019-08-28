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
import copy
import inspect
import fnmatch
# Local import
from . import tools
from . import debug
from . import heritage
from . import multiprocess
from . import env

class Module:
	##
	## @brief Module class represent all system needed for a specific
	## 	module like 
	## 		- type (bin/lib ...)
	## 		- dependency
	## 		- flags
	## 		- files
	## 		- ...
	##
	def __init__(self, file, module_name):
		## Remove all variable to prevent error of multiple deffinition of the module ...
		debug.verbose("Create a new module : '" + module_name + "'")
		self.origin_file=''
		self.origin_path=''
		# Name of the module
		self.name=module_name
		# Dependency list:
		self.depends = []
		self.define = []
		self.version = None
		self.full_name = "No Title"
		self.website = ""
		self.website_source = ""
		self.path = []
		self.data_path = []
		self.sample_path = []
		self.exclude_symbole = []
		self.file_patterns = []
		self.exclude_file = []
		self.authors = []
		
		# The module has been already build ...
		self.isbuild = False
		self.origin_file = file;
		self.origin_path = tools.get_current_path(self.origin_file)
		self.local_heritage = heritage.heritage(self, None)
		self.sub_heritage_list = None
	
	def __repr__(self):
		return "{doxy.Module:" + str(self.name) + "}"
	
	
	# call here to build the module
	def build(self, target, package_name):
		# ckeck if not previously build
		if target.is_module_build(self.name) == True:
			if self.sub_heritage_list == None:
				self.local_heritage = heritage.heritage(self, target)
			return copy.deepcopy(self.sub_heritage_list)
		# create the package heritage
		self.local_heritage = heritage.heritage(self, target)
		
		# build dependency before
		list_sub_file_needed_to_build = []
		self.sub_heritage_list = heritage.HeritageList()
		# optionnal dependency :
		for dep in self.depends:
			debug.debug("module: '" + str(self.name) + "'   request: '" + dep + "'")
			inherit_list = target.build(dep, package_name)
			# add at the heritage list :
			self.sub_heritage_list.add_heritage_list(inherit_list)
		package_version_string = tools.version_to_string(self.version);
		debug.print_element("Module", self.name, "-", package_version_string)
		
		filename_dox = os.path.join(target.get_final_path(), self.name + ".dox")
		
		debug.debug("Create doxygen file: '" + filename_dox + "'")
		data = tools.file_read_data(os.path.join(tools.get_current_path(__file__), "default_doxy_file.dox"))
		data += "\n"
		data += "# -----------------------------------\n"
		data += "# -- doxy footer and header\n"
		data += "# -----------------------------------\n"
		data += "HTML_HEADER            = " + os.path.join(tools.get_current_path(__file__), "doxygen-bootstrapped", "example-site", "header.html") + "\n"
		data += "HTML_FOOTER            = " + os.path.join(tools.get_current_path(__file__), "doxygen-bootstrapped", "example-site", "footer.html") + "\n"
		data += "HTML_EXTRA_STYLESHEET  = " + os.path.join(tools.get_current_path(__file__), "doxygen-bootstrapped", "customdoxygen.css") + "\n"
		data += "HTML_EXTRA_FILES       = " + os.path.join(tools.get_current_path(__file__), "doxygen-bootstrapped", "doxy-boot.js") + "\n"
		data += "\n"
		data += "# -----------------------------------\n"
		data += "# -- doxy auto-added section\n"
		data += "# -----------------------------------\n"
		data += 'PROJECT_NAME = "' + str(self.full_name) + '"\n'
		
		if self.version != None:
			data += 'PROJECT_NUMBER = "' + tools.version_to_string(self.version) + '"\n'
		
		data += 'OUTPUT_DIRECTORY = "' + str(os.path.join(target.get_final_path(), self.name)) + '"\n'
		data += 'GENERATE_TAGFILE = "' + str(os.path.join(target.get_final_path(), self.name + ".tag")) + '"\n'
		for elem in self.data_path:
			if len(elem) == 0:
				continue
			data += 'IMAGE_PATH += "'
			if elem[0] == "/":
				data += str(elem)
			else:
				data += os.path.join(tools.get_current_path(self.origin_file), elem)
			data += '"\n'
		
		for elem in self.sample_path:
			if len(elem) == 0:
				continue
			data += 'EXAMPLE_PATH += "'
			if elem[0] == "/":
				data += str(elem)
			else:
				data += os.path.join(tools.get_current_path(self.origin_file), elem)
			data += '"\n'
		
		for elem in self.path:
			if len(elem) == 0:
				continue
			data += 'INPUT += "'
			if elem[0] == "/":
				data += str(elem)
			else:
				data += os.path.join(tools.get_current_path(self.origin_file), elem)
			data += '"\n'
		
		for elem in self.exclude_symbole:
			if len(elem) == 0:
				continue
			data += 'EXCLUDE_SYMBOLS += "' + str(elem) + '"\n'
		
		for elem in self.file_patterns:
			if len(elem) == 0:
				continue
			data += 'FILE_PATTERNS += ' + str(elem) + '\n'
		
		for elem in self.exclude_file:
			if len(elem) == 0:
				continue
			data += 'EXCLUDE_PATTERNS += "' + str(elem) + '"\n'
		
		for elem in self.define:
			if len(elem) == 0:
				continue
			data += 'PREDEFINED += ' + str(elem) + '=1\n'
		
		for element in self.sub_heritage_list.list_heritage:
			data += "TAGFILES += " + os.path.join(target.get_final_path(), element.name + ".tag")
			if target.config["mode"] == "release":
				data += '=' + target.get_module(element.name).website
			else:
				data += '=' + os.path.join(target.get_final_path(), element.name, "html")
			data += "\n"
		data += '\n\n\n'
		tools.file_write_data(filename_dox, data)
		multiprocess.run_command("doxygen " + filename_dox)
		debug.debug("heritage: " + str(self.sub_heritage_list))
		self.sub_heritage_list.add_heritage(self.local_heritage)
		# return local dependency ...
		return copy.deepcopy(self.sub_heritage_list)
	
	# call here to clean the module
	def clean(self, target):
		# remove path of the lib ... for this targer
		pathbuild = os.path.join(target.get_final_path(), self.name)
		debug.info("remove path : '" + pathbuild + "'")
		tools.remove_path_and_sub_path(pathbuild)
	
	
	def set_version(self, val):
		self.version = tools.get_version_from_file_or_direct(self.origin_path, val)
	
	def set_authors(self, val):
		self.authors = tools.get_maintainer_from_file_or_direct(self.origin_path, val)
	
	def set_title(self, val):
		self.full_name = val
	
	def set_website(self, val):
		self.website = val
	
	def set_website_sources(self, val):
		self.website_source = val
	
	def add_path(self, list):
		tools.list_append_to(self.path, list, True)
	
	def add_sample_path(self, list):
		tools.list_append_to(self.sample_path, list, True)
	
	def add_data_path(self, list):
		tools.list_append_to(self.data_path, list, True)
	
	def add_depend(self, list):
		tools.list_append_to(self.depends, list, True)
	
	def add_module_define(self, list):
		tools.list_append_to(self.define, list, True)
	
	def add_exclude_symbols(self, list):
		tools.list_append_to(self.exclude_symbole, list, True)
	
	def add_exclude_file(self, list):
		tools.list_append_to(self.exclude_file, list, True)
	
	def add_file_patterns(self, list):
		tools.list_append_to(self.file_patterns, list, True)
	
	def print_list(self, description, input_list):
		if type(input_list) == list:
			if len(input_list) > 0:
				print('        ' + str(description))
				for elem in input_list:
					print('            ' + str(elem))
		else:
			print('        ' + str(description))
			print('            ' + str(input_list))
	
	def display(self):
		print('-----------------------------------------------')
		print(' package : "' + self.name + "'")
		print('-----------------------------------------------')
		print('    version:"' + str(self.version) + "'")
		print('    full name:"' + str(self.full_name) + "'")
		print('    path:"' + str(self.origin_path) + "'")
		print('    website:"' + str(self.website) + "'")
		print('    website source:"' + str(self.website_source) + "'")
		print('    path:"' + str(self.path) + "'")
		self.print_list('depends',self.depends)
		self.print_list('define',self.define)
		self.print_list('data_path',self.data_path)
		self.print_list('sample_path',self.sample_path)
		
		return True
	

module_list=[]
__start_module_name="_"

def import_path(path_list):
	global module_list
	global_base = env.get_build_system_base_name()
	debug.debug("MODULE: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove .py at the end:
		filename = filename[:-3]
		# Remove global base name:
		filename = filename[len(global_base):]
		# Check if it start with the local patern:
		if filename[:len(__start_module_name)] != __start_module_name:
			debug.extreme_verbose("MODULE:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
			continue
		# Remove local patern
		module_name = filename[len(__start_module_name):]
		debug.verbose("MODULE:     Integrate: '" + module_name + "' from '" + elem + "'")
		module_list.append([module_name, elem])
	debug.verbose("New list module: ")
	for elem in module_list:
		debug.verbose("    " + str(elem[0]))

def exist(target, name):
	global module_list
	for mod in module_list:
		if mod[0] == name:
			return True
	return False

def load_module(target, name):
	global module_list
	for mod in module_list:
		if mod[0] == name:
			sys.path.append(os.path.dirname(mod[1]))
			debug.verbose("import module : '" + env.get_build_system_base_name() + __start_module_name + name + "'")
			the_module_file = mod[1]
			the_module = __import__(env.get_build_system_base_name() + __start_module_name + name)
			# configure the module:
			if "create" in dir(the_module):
				tmp_element = the_module.create(target, name)
			else:
				debug.warning(" no function 'create' in the module : " + mod[0] + " from:'" + mod[1] + "'")
				continue
			# check if create has been done corectly
			if tmp_element == None:
				debug.debug("Request load module '" + name + "' not define for this platform")
			else:
				target.add_module(tmp_element)
				return tmp_element

def list_all_module():
	global module_list
	tmpListName = []
	for mod in module_list:
		tmpListName.append(mod[0])
	return tmpListName

def list_all_module_with_desc():
	global module_list
	tmpList = []
	for mod in module_list:
		sys.path.append(os.path.dirname(mod[1]))
		the_module = __import__(env.get_build_system_base_name() + __start_module_name + mod[0])
		tmpList.append({
		    "name":mod[0],
		    "description":" "
		    })
	return tmpList


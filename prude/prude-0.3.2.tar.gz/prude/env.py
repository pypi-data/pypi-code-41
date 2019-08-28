#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2017, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

# Local import
from . import debug
import os

system_base_name = "prude"

def set_system_base_name(val):
	global system_base_name
	system_base_name = val
	debug.debug("Set basename: '" + str(system_base_name) + "'")

def get_system_base_name():
	global system_base_name
	return system_base_name


def file_read_data(path):
	if not os.path.isfile(path):
		return ""
	file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

def read_file_property(folder):
	# parse the global .prude file
	filter_list = [{"check-capital":True}, [], []]
	list_files = os.listdir(folder)
	for ff_file in list_files:
		if     (     len(ff_file) >= 7 \
		         and ff_file[:7] == ".prude_") \
		   or ff_file == ".prude":
			pass
		else:
			continue
		debug.debug("Load config file:" + os.path.join(folder,ff_file))
		data = file_read_data(os.path.join(folder,ff_file))
		for elem in data.split("\n"):
			if elem == "":
				continue
			if elem[0] == "#":
				continue
			if elem[0] == "!":
				# specific control check
				if elem == "!NO_CAPITAL_LETTER":
					filter_list[0]["check-capital"] = False
				elif elem == "!CAPITAL_LETTER":
					filter_list[0]["check-capital"] = True
				else:
					debug.error("unknows parameter: '" + elem + "'")
				continue
			if elem[0] == "+":
				# check the full name:
				filter_list[1].append(elem[1:])
			else:
				filter_list[2].append(elem)
	debug.verbose("fulllist:" + str(filter_list))
	return filter_list



def get_local_filter(path_to_search):
	path_to_search = os.path.join(os.getcwd(), path_to_search)
	if os.path.exists(path_to_search) == False:
		return []
	
	# parse the global .prude file
	filter_list = [{"check-capital":True}, [], []]
	current_path = path_to_search
	while current_path != "/":
		list_files = os.listdir(current_path)
		debug.debug("read path: " + current_path)
		tmp_value = read_file_property(current_path)
		
		for key in tmp_value[0]:
			filter_list[0][key] = tmp_value[0][key]
		
		for elem in tmp_value[1]:
			if elem not in filter_list[1]:
				filter_list[1].append(elem)
		
		for elem in tmp_value[2]:
			if elem not in filter_list[2]:
				filter_list[2].append(elem.lower())
		
		if os.path.exists(os.path.join(current_path, ".prude")) == True:
			debug.debug("fulllist:" + str(filter_list))
			return filter_list
		current_path = os.path.dirname(current_path)
	debug.debug("fulllist (root):" + str(filter_list))
	return filter_list

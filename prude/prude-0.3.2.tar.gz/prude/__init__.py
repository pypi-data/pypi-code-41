#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2017, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import os
import sys
import fnmatch
import copy
from . import debug
from . import arg as arguments
from . import env
from . import tools
from . import module

myArgs = arguments.doxyArg()
myArgs.add(arguments.ArgDefine("h", "help", desc="Display this help"))
myArgs.add(arguments.ArgDefine("",  "version", desc="Display the application version"))
myArgs.add_section("option", "Can be set one time in all case")
myArgs.add(arguments.ArgDefine("v", "verbose", list=[["0","None"],["1","error"],["2","warning"],["3","info"],["4","debug"],["5","verbose"],["6","extreme_verbose"]], desc="display makefile debug level (verbose) default =2"))
myArgs.add(arguments.ArgDefine("C", "color", desc="Display makefile output in color"))
myArgs.add(arguments.ArgDefine("r", "recursive", desc="Recursive check of the paths"))

myArgs.add_section("cible", "generate in order set")
localArgument = myArgs.parse()

## Display the help of this makefile
def usage(full=False):
	color = debug.get_color_set()
	# generic argument displayed : 
	myArgs.display()
	print("	ex: " + sys.argv[0] + " myFile1.cpp")
	exit(0)

##
## @brief Display the version of this package.
##
def version():
	color = debug.get_color_set()
	import pkg_resources
	print("version: " + str(pkg_resources.get_distribution('prude').version))
	foldername = os.path.dirname(__file__)
	print("source folder is: " + foldername)
	exit(0)

def check_boolean(value):
	if    value == "" \
	   or value == "1" \
	   or value == "true" \
	   or value == "True" \
	   or value == True:
		return True
	return False


recursive = False;

# preparse the argument to get the verbose element for debug mode
def parseGenericArg(argument, active):
	debug.extreme_verbose("parse arg : " + argument.get_option_name() + " " + argument.get_arg() + " active=" + str(active))
	if argument.get_option_name() == "help":
		if active==False:
			usage()
		return True
	elif argument.get_option_name() == "version":
		if active == False:
			version()
		return True
	elif argument.get_option_name() == "recursive":
		if active==False:
			recursive = True;
		return True
	elif argument.get_option_name() == "verbose":
		if active==True:
			debug.set_level(int(argument.get_arg()))
		return True
	elif argument.get_option_name() == "color":
		if active==True:
			if check_boolean(argument.get_arg()) == True:
				debug.enable_color()
			else:
				debug.disable_color()
		return True
	return False

# parse default unique argument:
for argument in localArgument:
	parseGenericArg(argument, True)

actionDone = False;

summary = []

def recursive_get(path):
	out = []
	for root, directories, filenames in os.walk(path):
		for filename in filenames:
			#debug.info(os.path.join(root,filename))
			if     len(filename) > 2 \
			   and (    filename[-3:].lower() == ".d" \
			         or filename[-3:].lower() == ".o"):
				pass
			else:
				out.append(os.path.join(root,filename))
		for dir in directories:
			tmp = recursive_get(os.path.join(root,dir))
			for elem in tmp:
				out.append(elem)
	return out

# parse all argument
number_of_error = 0
for argument in localArgument:
	if parseGenericArg(argument, False) == True:
		continue
	else:
		argument_value = argument.get_arg()
		debug.debug("something request : '" + argument_value + "'")
		if argument.get_option_name() != "":
			debug.warning("Can not understand argument : '" + argument.get_option_name() + "'")
			usage()
			break;
		if os.path.isfile(argument_value) == True:
			# Single file:
			tmp_count_error = module.annalyse(argument_value)
			summary.append([argument_value, tmp_count_error])
			number_of_error += tmp_count_error
		else:
			# a full path
			if recursive == True:
				list_files = os.listdir(argument_value)
			else:
				list_files = recursive_get(argument_value)
			real_list = []
			for ff_file in list_files:
				if os.path.isfile(os.path.join(argument_value,ff_file)) == False:
					continue
				if     len(ff_file) > 3 \
				   and (    ff_file[-4:].lower() == ".cpp" \
				         or ff_file[-4:].lower() == ".hpp" \
				         or ff_file[-4:].lower() == ".c++" \
				         or ff_file[-2:].lower() == ".c" \
				         or ff_file[-4:].lower() == ".h++" \
				         or ff_file[-2:].lower() == ".h" \
				         or ff_file[-3:].lower() == ".hh" \
				         or ff_file[-3:].lower() == ".cc" \
				         or ff_file[-3:].lower() == ".py" \
				         or ff_file[-4:].lower() == ".lua" \
				         or ff_file[-3:].lower() == ".md"):
					real_list.append(os.path.join(argument_value,ff_file))
			# sort list to have all time the same order.
			real_list.sort()
			# TODO: Add filter if needed.
			for ff_file in real_list:
				debug.info("-----------------------------------------------")
				tmp_count_error = module.annalyse(ff_file)
				summary.append([ff_file, tmp_count_error])
				number_of_error += tmp_count_error
		actionDone = True

# if no action done : we do "all" ...
if actionDone == False:
	usage()
	exit(-1)

if number_of_error != 0:
	debug.info("Detected " + str(number_of_error) + " ERROR(s) on " + str(len(summary)) + " files")
	for elem in summary:
		if elem[1] != 0:
			debug.info(elem[0] + "\r\t\t\t\t\t\t [ERROR] " + str(elem[1]))
		else:
			debug.info(elem[0] + "\r\t\t\t\t\t\t [ OK  ]")
	exit(-1);

debug.info("[ OK  ]")
exit(0);

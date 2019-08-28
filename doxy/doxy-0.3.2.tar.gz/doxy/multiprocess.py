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
import threading
import time
import sys
import os
import subprocess
import shlex
# Local import
from . import debug
from . import tools
from . import env



def run_command(cmd_line, store_cmd_line="", store_output_file=""):
	global error_occured
	global exit_flag
	global current_id_execution
	global error_execution
	# prepare command line:
	args = shlex.split(cmd_line)
	debug.verbose("cmd = " + str(args))
	try:
		# create the subprocess
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		debug.error("subprocess.CalledProcessError : TODO ...")
	except:
		debug.error("Exception on : " + str(args))
	# launch the subprocess:
	output, err = p.communicate()
	if sys.version_info >= (3, 0):
		output = output.decode("utf-8")
		err = err.decode("utf-8")
	# store error if needed:
	tools.store_warning(store_output_file, output, err)
	# Check error :
	if p.returncode == 0:
		debug.debug(env.print_pretty(cmd_line))
		if output != "":
			debug.print_compilator(output)
		if err != "":
			debug.print_compilator(err)
	else:
		# if No ID : Not in a multiprocess mode ==> just stop here
		debug.debug(env.print_pretty(cmd_line), force=True)
		debug.print_compilator(output)
		debug.print_compilator(err)
		if p.returncode == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... ret : " + str(p.returncode))
	debug.verbose("done 3")
	# write cmd line only after to prevent errors ...
	tools.store_command(cmd_line, store_cmd_line)


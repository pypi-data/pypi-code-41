"""Dispatcher will be called upon successful evaluation of commands
entered to execute respective command.It includes Dispatch routines
- the actual functions that implement the command"""

import os
import getpass
from importlib import import_module
import sys
import socket
from datetime import datetime
import time
import subprocess
from command_dictionary import cmd_dict

"""This function will dynamically call respective required command modules
and call their fuctions according to the arguments entered"""


def run(args):
    command_name = args[0]
    this_module = sys.modules[__name__]
    # checking if the command is miscellaneous command
    if hasattr(this_module, command_name):
        getattr(this_module, command_name)(args)
    else:
        # dynamically importing the required module and calling run function
        imported_module = import_module('.' + command_name, 'commands')
        try:
            if(len(args) == 1):
                imported_module.run()
            elif(args[1] == "-h" or args[1] == "--help"):
                print(args[0] + " : " + cmd_dict.get(args[0]))
            elif (len(args) == 2):
                imported_module.run(args[1])
            elif (len(args) == 3):
                imported_module.run(args[1], args[2])
            elif (len(args) == 4):
                imported_module.run(args[1], args[2], args[3])
        except TypeError as e:
            print(e)
            print("Type help followed by the command for more help")
            print("\n")

# Micellaneous commands


def whoami(args):
    print(getpass.getuser())


def hostname(args):
    print(socket.gethostname())


def date(args):
    print(datetime.now())


def timeit(args):
    start = time.clock()
    command = args[1]
    curr_module = sys.modules[__name__]
    if hasattr(curr_module, command):
        getattr(curr_module, command)(args)
    else:
        imported_module = import_module('.' + command, 'commands')
        if(len(args) == 2):
            imported_module.run()
        elif (len(args) == 3):
            imported_module.run(args[2])
        elif (len(args) == 4):
            imported_module.run(args[2], args[3])
        elif (len(args) == 5):
            imported_module.run(args[2], args[3], args[4])
    end = time.clock()
    print(end - start)

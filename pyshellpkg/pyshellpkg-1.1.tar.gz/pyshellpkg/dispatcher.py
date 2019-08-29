import os
import getpass
from importlib import import_module
import sys
import socket
from datetime import datetime
import time
import subprocess


def run(args):
    command_name = args[0]
    thismodule = sys.modules[__name__]
    if hasattr(thismodule,command_name):
        getattr(thismodule, command_name)(args)
    else:
        imported_module = import_module('.' + command_name, 'commands')
        try:
            if(len(args)==1):
                imported_module.run()
            elif (len(args)==2):
                imported_module.run(args[1])
            elif (len(args)==3):
                imported_module.run(args[1],args[2])
            elif (len(args)==4):
                imported_module.run(args[1],args[2],args[3])
        except TypeError as e:
            print(e)
            print("Type help followed by the command for more help")
            print("\n")


def history(args):
    from pyreadline import Readline
    readline = Readline()
    print("hjhhjhj")
    for i in range(readline.get_current_history_length()):
        print("hjhhjhj")
        print(readline.get_history_item(i + 1))

def whoami(args):
    print(getpass.getuser())

def hostname(args):
	print(socket.gethostname())

def date(args):
    print(datetime.now())

def timeit(args):
    start = time.clock()
    command = args[1]
    currmodule = sys.modules[__name__]
    if hasattr(currmodule,command):
        getattr(currmodule, command)(args)
    else:
        imported_module = import_module('.' + command, 'commands')
        if(len(args)==2):
            imported_module.run()
        elif (len(args)==3):
            imported_module.run(args[2])
        elif (len(args)==4):
            imported_module.run(args[2],args[3])
        elif (len(args)==5):
            imported_module.run(args[2],args[3],args[4])
    end = time.clock()
    print(end - start)

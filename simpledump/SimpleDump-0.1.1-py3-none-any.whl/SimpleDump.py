# License MIT
#
# Authors: Vladimir Udartsev <v.udartsev@gmail.com>
#
# """Creating simple print of objects for better code debugging"""

from pprint import pprint
from inspect import getmembers
import sys


def var_dump(variable):
    """Print var data recursevly to console"""
    results = checkVar(variable)
    return results


def dump(variable):
    """Print var data recursevly to console"""
    results = checkVar(variable)
    return results


def dd(variable):
    """Print var data recursevly to console and exit program"""
    checkVar(variable)
    message = "\n/*****************************/"
    message += "\n/** EXITED BY dd() FUNCTION **/"
    message += "\n/*****************************/"
    message += "\n"
    sys.exit(style.RED(message))


def checkVar(variable):
    if type(variable) is str:
        data = style.YELLOW("\n(string) ")
        data += style.RESET(variable)
        data += "\n"
        print(data)
    elif type(variable) is bool:
        data = style.BLUE("\n(bool) ")
        data += style.RESET(variable)
        data += "\n"
        print(data)
    elif type(variable) is list:
        data = style.GREEN("\n(list,array) ")
        data += style.RESET(variable)
        data += "\n"
        print(data)
    elif type(variable) is int:
        data = style.MAGENTA("\n(int) ")
        data += style.RESET(variable)
        data += "\n"
        print(data)
    else:
        print(style.CYAN("\n(object)") + style.RESET(" "))
        data = getmembers(variable)
        pprint(data)
        print("\n")
    pass
    return data


# Group of Different functions for different styles
class style():
    def BLACK(x): return '\033[30m' + str(x)
    def RED(x): return '\033[31m' + str(x)
    def GREEN(x): return '\033[32m' + str(x)
    def YELLOW(x): return '\033[33m' + str(x)
    def BLUE(x): return '\033[34m' + str(x)
    def MAGENTA(x): return '\033[35m' + str(x)
    def CYAN(x): return '\033[36m' + str(x)
    def WHITE(x): return '\033[37m' + str(x)
    def UNDERLINE(x): return '\033[4m' + str(x)
    def RESET(x): return '\033[0m' + str(x)

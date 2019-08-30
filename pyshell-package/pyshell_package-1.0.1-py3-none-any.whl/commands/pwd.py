# pwd--- to get current working directory
# importing required in-built module
import os


def run():
    """ this function is called when pwd is entered in PyShell"""
    varpwd = os.getcwd()
    print(varpwd)

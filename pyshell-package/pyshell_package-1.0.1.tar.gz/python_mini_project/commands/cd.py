# cd---- change directory command
# importing required in-built modules
import os
import sys


def run(destdir):
    """ this function is called when cd along with required
    argument are entered in PyShell"""
    var = os.getcwd()
    try:
        os.chdir(destdir)       # change the directory as asked by the user
    except Exception:                     # handle exception, if occurred
        from extern import extern_var
        print(extern_var.get('not_found'), sys.exc_info())
    finally:                    # returns the previous directory, incase needed
        return var

import os
import sys

def run(destdir):
    var = os.getcwd()
    try:
        os.chdir(destdir)
    except:
         print("Something wrong with specified directory.Exception- ", sys.exc_info())
    finally:
        return var

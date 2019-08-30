# rmdir--- to remove directory
# importing required in-built module
import os


def run(path):
    """ this function is called when rmdir along with required argument are
    entered in PyShell"""
    try:
        os.rmdir(path)
        print("Directory %s has been removed successfully" % path)
    # handles exception
    except OSError:
        print("Directory %s can not be removed as it is not empty" % path)

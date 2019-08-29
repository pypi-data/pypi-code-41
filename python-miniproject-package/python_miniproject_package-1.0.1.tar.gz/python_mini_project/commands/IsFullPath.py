import os


def isFullPath(path):
    fullpath = path.split('\\')
    if(len(fullpath) > 1):
        return True
    else:
        return False

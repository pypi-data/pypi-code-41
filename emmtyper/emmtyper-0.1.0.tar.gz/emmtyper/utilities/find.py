'''
Define a wrapper function to find files in the package folder
'''
import os


def find(filename, path):
    '''
    Given a filename and a path, walk all files and subfolders of path trying
    to find an exact match to filename.
    '''
    for root, dirs, files in os.walk(os.path.dirname(path), topdown=True):
        for name in files:
            if name == filename:
                return os.path.join(root, name)

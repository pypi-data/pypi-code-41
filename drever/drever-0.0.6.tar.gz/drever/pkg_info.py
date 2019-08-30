'''
Created on Apr 4, 2019

Package Information Module

@author: baumannt
'''

MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 6


def get_version():
    '''
    Getter for version string of package.

    Returns:
    str:Version Number
    '''

    version_str = '.'.join(
        [str(MAJOR_VERSION), str(MINOR_VERSION), str(PATCH_VERSION)])
    return version_str


def print_version():

    ''' Prints version on stdout '''

    print("Version: " + get_version())

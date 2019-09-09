'''
Created on Apr 9, 2019

@author: hammonds
'''
try:
    from configparser import ConfigParser     # For Python 3
except ImportError:
    from ConfigParser import ConfigParser     #For Python 2
from os.path import expanduser, join, exists
from fileinput import filename

FILENAME_STR = "filename"
FILE_SECTION = "file"
LAST_DIRECTORY_STR = "lastDirectory"

class MinixsConfigParser(ConfigParser):
    
    def __init__(self, *args, **kwargs):
        filename = None
        homeDirectory = expanduser("~")
        if (FILENAME_STR in kwargs.items()):
            filename = kwargs[FILENAME_STR]
            if not exists(filename):
                raise Exception("Configuration file not found: %s" % filename)
            del kwargs[FILENAME_STR]
        else:
            filename = join(homeDirectory, "minixs.conf")
            
        ConfigParser.__init__(self, *args, **kwargs)
        self.configFileName = filename
        if not exists(self.configFileName):
            self.add_section(FILE_SECTION)
            self.set(FILE_SECTION,LAST_DIRECTORY_STR, homeDirectory)
            with open(self.configFileName, "w") as configFile:
                self.write(configFile)
                
        with open(self.configFileName, "r") as configFile:
            self.read(configFile)

    def updateFile(self):
        with open(self.configFileName, "w") as configFile:
            self.write(configFile)
        
    def getLastFilePath(self):
        self.read(self.configFileName)
        
        return self.get(FILE_SECTION, LAST_DIRECTORY_STR)
        
if __name__ == '__main__':
    pass
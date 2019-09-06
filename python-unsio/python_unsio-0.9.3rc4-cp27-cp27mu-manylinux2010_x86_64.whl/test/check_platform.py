#!/usr/bin/env python
from __future__ import print_function

import platform
import sys

class CPlateform:
    """
    Detect running platform
    """
    __fdout=None # file descriptor
    __out=None   # file name
    __is_open=False # out file is not open
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 
    def __init__(self,out=None, fdout=None):
        """
        Set file descriptor to save platform information

        """
        self.__fdout = fdout
        self.__out   = out
        
        if (fdout is None and out is not None): # open a new file
            try:
                self.__fdout=open(out,"w")
                self.__is_open=True
            except:
                print("Impossible to write into file file[%s]\n"%(out))
                sys.exit()
        else :
            if (fdout is None and out is None) : # sys.stderr defaul
                self.__fdout=sys.stderr # default file desc if fdout is None
                
                
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # display
    
    def display(self):
        """
        Display platform information
        """
        print("""
Python version    : %s
dist              : %s
linux_distribution: %s
system            : %s
machine           : %s
platform          : %s
version           : %s
mac_ver           : %s
uname             : %s
        """ % (
        sys.version.split('\n'),
        str(platform.dist()),
        self.__linux_distribution(),
        platform.system(),
        platform.machine(),
        platform.platform(),
        platform.version(),
        platform.mac_ver(),
        platform.uname(),
        ),
        file=self.__fdout)
        if self.__is_open:
            self.__fdout.close()
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # __linux_distribution

    def __linux_distribution(self):
        try:
            return platform.linux_distribution()
        except:
            return "N/A"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# commandLine, parse the command line
def commandLine():
    import argparse
    # help
    parser = argparse.ArgumentParser(description="Print info on platform",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # options
    parser.add_argument('--out', help='save info in outfilename, if None on screen', type=str, default=None)

    args=parser.parse_args()
    process(args)
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# commandLine, parse the command line
def process(args):
    info=CPlateform(args.out)
    info.display()
    

# -----------------------------------------------------
# main program
if __name__ == '__main__':
  commandLine()


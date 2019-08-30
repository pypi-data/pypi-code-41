'''
Created on Apr 12, 2019

Python __init__

@author: baumannt
'''
import os
from vunit import VUnit

from drever import pkg_info

__version__ = pkg_info.get_version()

VHDL_LIBRARY_NAME = "drever"
VHDL_SRC_DIR = os.path.join(__path__[0], "vhdl/**/*.vhd")


def add_drever_hdl_sources(vunit):  # pragma: no cover
    '''
    Add Drever HDL sources to VUnit project.
    '''
    drever_lib = vunit.add_library(VHDL_LIBRARY_NAME)
    drever_lib.add_source_files(VHDL_SRC_DIR, vhdl_standard="2008")

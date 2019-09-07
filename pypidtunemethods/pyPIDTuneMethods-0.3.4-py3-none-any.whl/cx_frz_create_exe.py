# -*- coding: utf-8 -*-

# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
import os
from cx_Freeze import setup, Executable
import scipy, guidata, guiqwt

# include files
includefiles_list=[]
# scipy
scipy_path = os.path.dirname(scipy.__file__)
includefiles_list.append(scipy_path)
# guidata
guidata_path = os.path.dirname(guidata.__file__)
includefiles_list.append(guidata_path)
# guiqwt
guiqwt_path = os.path.dirname(guiqwt.__file__)
includefiles_list.append(guiqwt_path)

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
		'includes': 'atexit',
        'excludes': ['Tkinter', 'collections.abc'],
		'packages': [],
		'include_files': includefiles_list
    }
}

executables = [
    Executable('PIDTuneMethods.py', base=base)
]

setup(name='pyPIDTuneMethods',
      version='0.3.1',
      description='PIDTuneMethods - PID Tune Methods for first order and integrating processes',
      options=options,
      executables=executables
      )

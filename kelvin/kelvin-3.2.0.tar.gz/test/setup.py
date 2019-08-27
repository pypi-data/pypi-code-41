
import sys
from os.path import abspath, join, dirname, isdir
from distutils.core import setup
from distutils.util import get_platform

# Use the source directory to make this easy to test.  You must run 'setup.py build' after
# modifying the C++ code, but not after modifying the Python code in the kelvin directory.

path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, path)

import kelvin

setup(
    name='hello',
    version='1.2.3-b4',
    description = 'Kelvin test file',
    cmdclass={
        'freeze':  kelvin.FreezeCommand,
        'freezew': kelvin.FreezeCommand,
        },

    options={
        # Freezes the hello.py script into a console application.
        'freeze' : {
            'script'       : 'hello.py',          # the startup script, run as __main__
            'subsystem'    : 'console',           # console or windows
            'includes'     : 'dynload',           # modules to include that aren't picked up automatically
            'excludes'     : 'pyexpat gzip',      # modules to exlude
            'dll_excludes' : 'tcl85.dll tk85.dll msvcr90.dll', # extensions and dependencies to exclude

            # 0x0409 is English
            'version_strings' : { 0x0409: { 'CompanyName': 'This Company'} },

            # Adding the same file twice, once with no changes to make sure the path is used and once overriding the
            # destination name to make sure that works.
            'extra' : [ 'data\\test.txt',               # put this file into the archive as /data/test.txt
                        ('data\\test.txt', 'test1.txt') # put the same file in as /test1.txt
                        ]
            },

        # Freezes the winhello.py script into a Windows application.
        'freezew' : {
            'script'       : 'winhello.py',       # the startup script, run as __main__
            'subsystem'    : 'windows',           # console or windows
            'excludes'     : 'pyexpat gzip',      # modules to exlude
            'dll_excludes' : 'tcl85.dll tk85.dll msvcr90.dll', # extensions and dependencies to exclude
            },
        }
)


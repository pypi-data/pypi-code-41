#!C:\Python37-32\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'squp==0.1.6','console_scripts','squp'
__requires__ = 'squp==0.1.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('squp==0.1.6', 'console_scripts', 'squp')()
    )

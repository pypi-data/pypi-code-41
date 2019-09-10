#!/usr/bin/env python3
from setuptools import setup, Extension


__version__ = '0.0.1'

long_description = '''
This is a small Python3 extension which sends arbitrary commands to SCSI devices, via the Linux SCSI Generic driver, which provides the SG_IO ioctl for this purpose.
Basically, the module includes three methods to read and write, which
allow you to issue commands to SCSI devices and read and write
accompanying data. If an OS error occurs, the OSError exception will
be raised, while if a SCSI error occurs, the py3_sg.SCSIError exception
will be raised.
'''

setup(
      name = "py3_sg",
      version = __version__,
      ext_modules=[
        Extension("py3_sg", ["src/py3_sg.c"])
        ],
      description = 'Python3 SCSI generic library',
      long_description = long_description,
      author = 'Zaman',
      author_email = '7amaaan@gmail.com',
      url = 'https://github.com/7aman/py3_sg',
      license = 'GPLv3',
      classifiers = ['Topic :: System :: Hardware'],
)                                                                                                  

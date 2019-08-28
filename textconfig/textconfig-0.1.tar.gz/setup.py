# setup.py Install script for textconfig.py Copyright (C) 2011 George
# Vlahavas E-mail: vlahavas ~ at ~ gmail ~ dot ~ com

# This software is licensed under the terms of the GPLv3 license.

import sys
from setuptools import setup
from textconfig import __version__ as VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name = 'textconfig',
      version = VERSION,
      description = 'Simple text configuration file reading/writing',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      license = 'GPLv3',
      platforms = ["Platform Independent"],
      author = 'George Vlahavas',
      author_email = 'vlahavas@gmail.com',
      url = 'https://github.com/gapan/textconfig',
      py_modules = ['textconfig'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries',
        ],
     )

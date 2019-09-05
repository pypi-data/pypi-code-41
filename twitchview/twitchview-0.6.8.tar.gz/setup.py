#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
setup.py for the Python packager

Based on https://github.com/pypa/sampleproject/blob/master/setup.py
"""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path
import os
from twitchview import main

here = path.abspath(path.dirname(__file__))
print(here)
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''
try:
    TODO = open(os.path.join(here, 'TODO.txt')).read()
except IOError:
    TODO = ''
try:
    AUTHORS = open(os.path.join(here, 'CONTRIBUTING.amd')).read()
except IOError:
    AUTHORS = ''
try:
    CHANGES = open(os.path.join(here, 'CHANGELOG')).read()
except IOError:
    CHANGES = ''

long_description = README + '\n\n' + TODO + '\n\n' + AUTHORS + '\n\n' + CHANGES

print(os.listdir('.'))  # DEBUG

setup(
    name='twitchview',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=main.__version__,
    description='Simple program by python for watching favorite twitch channels',
    long_description=long_description,
    url='https://gitlab.com/aspellip/twitchview',
    bugtrack_url='https://gitlab.com/aspellip/twitchview/issues',
    author='Aspel',
    author_email='aspel@ukr.net',
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        'Programming Language :: Python :: 3',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities"
    ],
    keywords='twitch',
    packages=['twitchview'],
    entry_points={
          "gui_scripts": ["twitchview=twitchview.main:main"]
      },
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.ico', '*.xbm', '*.example', '*.rst', '*.txt', '*.pyw'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
    python_requires=">=3",
    install_requires=['m3u8', 'Pillow']
    # Actually also requires numpy, scipy and numpy but I don't want to force
    # pip to install these since pip is bad at that for those packages.
)

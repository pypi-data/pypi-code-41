#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'ftdi_serial'
DESCRIPTION = 'A Windows-only serial library that uses the FTDI driver for more reliable serial communications.'
URL = 'https://gitlab.com/ada-chem/ftdi_serial'
EMAIL = 'sesan@v13inc.com'
AUTHOR = 'Sean Clark'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.4'

# What packages are required for this module to be executed?
REQUIRED = [
    'pypiwin32', 'janus', 'ftd2xx', 'pyserial'
]

REQUIRED_REPOS = [
]

# What packages are optional?
EXTRAS = {
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    py_modules=['ftdi_serial', '__version__'],
    install_requires=REQUIRED,
    dependency_links=REQUIRED_REPOS,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
)
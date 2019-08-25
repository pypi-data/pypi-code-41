#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup for flask-easylog
"""

import os
from setuptools import setup, find_packages

__version_info__ = (1, 0, 0)
VERSION = '.'.join([str(val) for val in __version_info__])
NAME = "flask-easylog"
DESC = "flask_easylog extension for flask application"
URLPKG = "https://github.com/fraoustin/flask-easylog.git"

HERE = os.path.abspath(os.path.dirname(__file__))

# README AND CHANGES
with open(os.path.join(HERE, 'README.rst')) as readme:
    with open(os.path.join(HERE, 'CHANGES.rst')) as changelog:
        LONG_DESC = readme.read() + '\n\n' + changelog.read()
# REQUIREMENTS
with open('REQUIREMENTS.txt') as f:
    REQUIRED = f.read().splitlines()
# CLASSIFIERS
with open('CLASSIFIERS.txt') as f:
    CLASSIFIED = f.read().splitlines()
# AUTHORS
with open('AUTHORS.txt') as f:
    DATA = f.read().splitlines()
    AUTHORS = ','.join([i.split('::')[0] for i in DATA])
    AUTHORS_EMAIL = ','.join([i.split('::')[1] for i in DATA])

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    author=AUTHORS,
    author_email=AUTHORS_EMAIL,
    description=DESC,
    long_description=LONG_DESC,
    include_package_data=True,
    install_requires=REQUIRED,
    url=URLPKG,
    classifiers=CLASSIFIED,
    entry_points={},
    zip_safe=False,
    platforms='any'
)

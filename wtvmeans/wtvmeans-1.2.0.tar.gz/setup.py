#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@author: asr
"""

from setuptools import setup
import os

VERSION = '1.2.0'
WD = os.path.dirname(os.path.abspath(__file__))


def update_package_version_metadata():
    file = os.path.join(WD, 'wtvmeans/__init__.py')
    bak = file + '.bak'

    # backup
    raw = open(file, 'r').read()
    try:
        with open(bak, 'x') as backup:
            backup.write(raw)
    except FileExistsError:
        with open(bak, 'w') as backup:
            backup.write(raw)

    new_raw = ''
    for line in raw.split('\n'):
        if line.startswith('__version__'):
            new_raw += '__version__ = "{:s}"\n'.format(VERSION)
        else:
            new_raw += line + '\n'
    with open(file, 'w') as new:
        new.write(new_raw)


update_package_version_metadata()

setup(
    name='wtvmeans',
    version=VERSION,
    description='A library implementing k-means wrappers',
    author='Alban Siffer',
    author_email='alban.siffer@irisa.fr',
    license='GPLv3',
    packages=['wtvmeans'],
    zip_safe=False,
)

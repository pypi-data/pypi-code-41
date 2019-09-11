#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Setup MeX project.

# File: setup.py.
# Author: Tomás Vírseda
# License: GPL v3
# Description: setup.py tells you that the module/package you are about
# to install has been packaged and distributed with Distutils, which is
# the standard for distributing Python Modules.
"""

import os
import glob
from setuptools import setup


with open('README') as f:
    long_description = f.read()


def add_data(root_data):
    """Add data files from a given directory."""
    dir_files = []
    resdirs = set()
    for root, dirs, files in os.walk(root_data):
        resdirs.add(os.path.realpath(root))

    resdirs.remove(os.path.realpath(root_data))

    for directory in resdirs:
        files = glob.glob(directory+'/*')
        relfiles = []
        for thisfile in files:
            if not os.path.isdir(thisfile):
                relfiles.append(os.path.relpath(thisfile))
        if len(files) > 0:
            dir_files.append((os.path.relpath(directory), relfiles))

    return dir_files


data_files = add_data('kb4it/resources')
# ~ pprint.pprint (data_files)

setup(
    name='kb4it',
    version='0.6.0.1',
    author='Tomás Vírseda',
    author_email='tomasvirseda@gmail.com',
    url='https://github.com/t00m/KB4IT',
    description='A static website generator based on Asciidoc sources \
    and Asciidoctor processor and publishing toolchain.',
    long_description=long_description,
    download_url='https://github.com/t00m/KB4IT/archive/master.zip',
    license='GPLv3',
    packages=['kb4it', 'kb4it.core', 'kb4it.services'],
    # distutils does not support install_requires, but pip needs it to be
    # able to automatically install dependencies
    install_requires=[
        'rdflib',
    ],
    include_package_data=True,
    data_files=data_files,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'kb4it = kb4it.kb4it:main',
            ],
        },
)

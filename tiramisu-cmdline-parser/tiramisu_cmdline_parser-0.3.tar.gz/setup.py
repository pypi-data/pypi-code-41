#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
from tiramisu_cmdline_parser import __version__


PACKAGE_NAME = os.environ.get('PACKAGE_DST', 'tiramisu_cmdline_parser')

setup(
    version=__version__,
    author="Tiramisu's team",
    author_email='gnunux@gnunux.info',
    name=PACKAGE_NAME,
    description="command-line parser using Tiramisu.",
	url='https://framagit.org/tiramisu/tiramisu-cmdline-parser',
    license='GNU Library or Lesser General Public License (LGPL)',
    install_requires=["tiramisu_api>=0.1"],
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
	    "Natural Language :: English",
        "Natural Language :: French",
	    ],
	long_description="""\
tiramisu-cmdline-parser
---------------------------------

Python3 parser for command-line options and arguments using Tiramisu engine.
""",
    include_package_data=True,
    packages=find_packages(include=['tiramisu_cmdline_parser'])
)

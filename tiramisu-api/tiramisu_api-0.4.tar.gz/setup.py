#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
from tiramisu_api import __version__


PACKAGE_NAME = os.environ.get('PACKAGE_DST', 'tiramisu_api')

setup(
    version=__version__,
    author="Tiramisu's team",
    author_email='gnunux@gnunux.info',
    name=PACKAGE_NAME,
    description="a subset of Tiramisu API",
	url='https://framagit.org/tiramisu/tiramisu-api-python',
    license='GNU Library or Lesser General Public License (LGPL)',
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
	    "Natural Language :: English",
        "Natural Language :: French",
	    ],
	long_description="""\
tiramisu-api-python
-------------------

A subset of Tiramisu API that work with config.option.dict() structure.
It could be use remotly.
""",
    include_package_data=True,
    packages=find_packages(include=['tiramisu_api'])
)

#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
	name="rknn-test",
	version="0.0.2",
	author="oliver peng",
	author_email="oliver.peng@rock-chips.com",
	description="for test",
	long_description=open("README").read(),
	license="MIT",
	url="https://github.com/silyman1/microblog",
	packages=['rknn'],
	install_requires=[
		"lxml"
		],
	classifiers=[
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Text Processing :: Indexing",
		"Topic :: Utilities",
		"Topic :: Internet",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Programming Language :: Python",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3",
	],
)

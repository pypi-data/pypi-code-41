#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from distutils.core import setup


def publish():
	"""Publish to PyPi"""
	os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
	publish()
	sys.exit()

required = []

# if python > 2.6, require simplejson

setup(
	name='parsejson',
	version='0.0.2',
	description='parse json file or strings',
	author='ludr',
	author_email='ludongran123@163.com',
	url='http://www.luima.ml',
	packages= [
		'parsejson',
	],
	install_requires=required,
	license='ISC',
	classifiers=[
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
	        'Programming Language :: Python :: 3.6'
		# 'Programming Language :: Python :: 3.1',
	],
)

#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__      = "Ricardo Ribeiro"
__credits__     = ["Ricardo Ribeiro"]
__license__     = "MIT"
__maintainer__  = "Ricardo Ribeiro"
__email__       = "ricardojvr@gmail.com"
__status__      = "Development"


from setuptools import setup, find_packages
import re, os

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PACKAGE_PATH, 'mcvapi','__init__.py'), 'r') as fd:
    content = fd.read()
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)


setup(

	name				='Modular computer vision API',
	version 			=version,
	description 		="""""",
	author  			='Ricardo Ribeiro',
	author_email		='ricardojvr@gmail.com',
	license 			='MIT',
	url='https://bitbucket.org/fchampalimaud/mcv-api',
	
	packages=find_packages(),
)
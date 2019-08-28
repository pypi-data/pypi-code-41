#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

from setuptools import setup
import os

def readme():
	with open('README.rst') as f:
		return f.read()


def read_version_file():
	if not os.path.isfile("version.txt"):
		return ""
	file = open("version.txt", "r")
	data_file = file.read()
	file.close()
	if len(data_file) > 4 and data_file[-4:] == "-dev":
		data_file = data_file[:-4]
	return data_file

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
setup(name='doxy',
      version=read_version_file(),
      description='Doxy is a simple wrapper over doxygen to generate multiple documentation for c++ library',
      long_description=readme(),
      url='http://github.com/HeeroYui/doxy',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='APACHE-2',
      packages=['doxy'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Compilers',
      ],
      keywords='documentation over doxygen',
      scripts=['bin/doxy'],
      # Does not work on MacOs
      #data_file=[
      #    ('/etc/bash_completion.d', ['bash-autocompletion/lutin']),
      #],
      include_package_data = True,
      zip_safe=False)

#To developp: sudo ./setup.py install
#             sudo ./setup.py develop
#TO register all in pip: ./setup.py register sdist upload


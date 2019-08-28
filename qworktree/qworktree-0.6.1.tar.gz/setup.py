#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2019, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from setuptools import setup
import os

def readme():
	with open('README.md') as f:
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
setup(name='qworktree',
      version=read_version_file(),
      description='qworktree generator of main Qt .pro file for a full worktree',
      long_description=readme(),
      url='http://github.com/HeeroYui/qworktree',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='MPL-2',
      packages=['qworktree'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'
      ],
      long_description_content_type="text/markdown",
      keywords='qmake worktree build qt',
      scripts=['bin/qworktree'],
      # Does not work on MacOs
      #data_file=[
      #    ('/etc/bash_completion.d', ['bash-autocompletion/lutin']),
      #],
      install_requires=[
          'lxml',
          'realog',
      ],
      include_package_data = True,
      zip_safe=False)

#To developp: sudo ./setup.py install
#             sudo ./setup.py develop
#TO register all in pip: use external tools:
#  pip install twine
#  # create the archive
#  ./setup.py sdist
#  twine upload dist/*


#!/usr/bin/env python

import re
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


CURDIR = dirname(abspath(__file__))

CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3
Topic :: Software Development :: Testing
Framework :: Robot Framework :: Library
'''.strip().splitlines()
with open(join(CURDIR, 'version.py'), encoding="utf-8") as f:
    VERSION = re.search("__version__ = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'requirements.txt')) as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='rbf',
    version=VERSION,
    description="Robot Framework test library for automation of Web, REST APIs, SOAP Services, zOS, FTP, DB, Desktop Applications",
    author="Rakesh Ummadisetty",
    author_email='rakesh.ummadisetty@dnb.no',
    url='https://AB62031@develop.dnb.no/git/scm/ab/4748-dnb_rbf-library.git',
    license          = 'Apache License 2.0',
    keywords         = 'robotframework testing testautomation',
    platforms        = 'any',
    install_requires = REQUIREMENTS,  
    classifiers=CLASSIFIERS,
    packages=['rbfFTP', 'rbfZOS', 'rbfREST', 'rflint', 'rflint.rules', 'rflint.parser', 'rbfWEB', 'rbfWEB.base', 'rbfWEB.keywords', 'rbfWEB.locators', 'rbfWEB.utils', 'rbfWEB.utils.events', 'rbfDB', 'rbfDesktop', 'rbfDesktop.keywords', 'rbfDesktop.keywords.items', 'rbfDesktop.utils', 'rbfDataDriver', 'rbfMetrics', 'rbfHTTP', 'rbfExcel', 'rbfSlack', 'rbfVideoRecorder'],
    package_data={"rbfDesktop": ["bin/*.dll"]},
    include_package_data=True,
    entry_points={
          'console_scripts': [
              'robotmetrics=rbfMetrics.runner:main',
          ]
      }     
)

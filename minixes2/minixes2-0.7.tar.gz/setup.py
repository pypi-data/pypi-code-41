'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from setuptools import setup, find_packages
import minixs
# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='minixes2',
      version=minixs.__version__,
      description='Python program to process MiniXES data from sector 20',
      long_description = long_description,
      long_description_content_type='text/markdown',
      author = 'Brian Mattern, John Hammonds',
      author_email = 'JPHammonds@anl.gov',
      maintainer = 'John Hammonds',
      maintainer_email = 'JPHammonds@anl.gov',
      
      url = '',
      packages = find_packages() ,
#       include_package_data=True,
      package_data = {},
      install_requires = [],
      license = 'See LICENSE File',
      platforms = 'any',
      scripts = ['bin/process_rixs',
               'bin/process_xes',
               'bin/run_calibrate.bat',
               'bin/run_calibrate',
               'bin/setup_rixs.bat']
      )

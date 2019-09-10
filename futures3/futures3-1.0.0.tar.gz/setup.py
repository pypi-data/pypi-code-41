#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import os.path
import sys

if sys.version_info[0] < 3:
    print('This package does not work on Python 2.\n',
          file=sys.stderr)
    sys.exit(1)

extras = {}
try:
    from setuptools import setup
    extras['zip_safe'] = False
except ImportError:
    from distutils.core import setup

here = os.path.dirname(__file__)
with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()

setup(name='futures3',
      version='1.0.0',
      description='The latest version for concurrent.futures package from Python 3',
      long_description=readme,
      author='Brian Quinlan',
      author_email='brian@sweetapp.com',
      maintainer=u'Mihai Pârvu',
      maintainer_email='mihaiparvu90@gmail.com',
      url='https://github.com/mihaiparvu/futures3',
      packages=['futures3'],
      python_requires='>3',
      license='PSF',
      classifiers=['License :: OSI Approved :: Python Software Foundation License',
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3 :: Only'],
      **extras
      )

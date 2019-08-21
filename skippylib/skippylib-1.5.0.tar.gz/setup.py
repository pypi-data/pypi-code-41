#!/usr/bin/env python

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


__author__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2016, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"

__project__ = 'skippylib'
__description__ = "Python module and a Tango Device Server to gain control " \
                  "to instruments that support the scpi protocol. Brother " \
                  "project of the scpilib."
__longDesc__ = """
This module has been developed to provide access to instruments that listen 
for SCPI protocol connections. It also provides a Tango Device Server.

This code is the natural evolution of previous device servers that had provided
many functionalities to, with this device, merge them together and make easy
to develop many more.

See more details in the doc directory of the sources repository.
"""
__url__ = "https://github.com/srgblnch/skippy"
# we use semantic versioning (http://semver.org/) and we update it using the
# bumpversion script (https://github.com/peritus/bumpversion)
__version__ = '1.5.0'


from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: '
    'GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ]


setup(name=__project__,
      license=__license__,
      description=__description__,
      long_description=__longDesc__,
      version=__version__,
      author=__author__,
      author_email=__email__,
      classifiers=classifiers,
      packages=find_packages(),
      url=__url__,
      entry_points={
          'console_scripts': ['Skippy=skippy.skippy:main']
          }
      )

# for the classifiers review see:
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
#
# Development Status :: 1 - Planning
# Development Status :: 2 - Pre-Alpha
# Development Status :: 3 - Alpha
# Development Status :: 4 - Beta
# Development Status :: 5 - Production/Stable

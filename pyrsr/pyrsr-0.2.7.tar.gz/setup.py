#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyrsr, A package providing relative spectral response functions for remote sensing instruments.
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("pyrsr/version.py") as version_file:
    exec(version_file.read(), version)

requirements = ['numpy', 'pandas', 'matplotlib', 'scipy']

setup_requirements = ['setuptools-git']  # needed for package_data version controlled by GIT

test_requirements = ['coverage', 'nose', 'nose-htmloutput', 'rednose']


setup(
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A package providing relative spectral response functions for remote sensing instruments.",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    package_dir={'pyrsr': 'pyrsr'},
    include_package_data=True,
    # NOTE: if the 'package_data' files are not under CVS or Subversion version control, we need setuptools-git here,
    #       otherwise they are not included in the PyPi upload content
    package_data={"pyrsr": ["data/**/**/*"]},
    keywords=['pyrsr', 'relative spectral response', 'remote sensing', 'sensors'],
    name='pyrsr',
    packages=find_packages(exclude=['tests*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitext.gfz-potsdam.de/geomultisens/pyrsr',
    version=version['__version__'],
    zip_safe=False,
)

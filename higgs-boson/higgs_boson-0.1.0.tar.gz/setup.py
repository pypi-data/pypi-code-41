# This file is part of Higgs Boson.
#
# Copyright (c) BitBoson
#
# Higgs Boson is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Higgs Boson is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Higgs Boson.  If not, see <https://www.gnu.org/licenses/>.
#
# Written by:
#     - Tyler Parcell <OriginLegend>
#

from setuptools import setup

VERSION = '0.1.0'

setup(
    name='higgs_boson',
    version=VERSION,
    py_modules=['higgs_boson'],
    packages=['builder'],
    license='GNU Lesser General Public License',
    author='BitBoson',
    author_email='development@bitboson.com',
    description='Higgs Boson Build System Project for Managing C++ builds and tests',
    entry_points={
        'console_scripts': ['higgs-boson=higgs_boson:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3 :: Only'
    ]
)

"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.
Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

from setuptools import setup, find_packages

from pymbs.__version__ import __version__, _version_min_python_

with open("README.rst", "r") as fh:
    long_description = fh.read()

required = [
    "numpy>=1.16.4",
    "pandas>=0.25.0",
]

setup(
    name='pymbs',
    version=__version__,
    python_requires=f">={_version_min_python_}",
    install_requires=required,

    packages=find_packages(),

    license='AGPLv3',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: "
        "GNU Affero General Public License v3 or later (AGPLv3+)",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],

    url='https://pypi.org/project/pymbs/',
    author="Brian Farrell",
    author_email="brian.farrell@me.com",
    description="A library for use in modeling Mortgage-Backed Securities.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    keywords="financial modeling analysis mortgage securities",
    zip_safe=False,
)

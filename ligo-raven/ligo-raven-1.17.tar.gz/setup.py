#!/usr/bin/python

#
# Project Librarian: Alex Urban
#              Graduate Student
#              UW-Milwaukee Department of Physics
#              Center for Gravitation & Cosmology
#              <alexander.urban@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from setuptools import setup, find_packages


setup(
    name='ligo-raven',
    version='1.17',
    url='http://gracedb.ligo.org',
    author='Alex Urban',
    author_email='alexander.urban@ligo.org',
    maintainer="Brandon Piotrzkowski",
    maintainer_email="brandon.piotrzkowski@ligo.org",
    description='Low-latency coincidence search between external triggers and GW candidates',
    license='GNU General Public License Version 3',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"
    ),
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    namespace_packages=['ligo'],
    scripts=[
        'bin/raven_coinc_search_gracedb',
        'bin/raven_fetch_external_triggers',
        'bin/raven_file_cache_monitor',
        'bin/raven_gcn_web_scraper',
        #'bin/raven_grb_pop_from_gwinj'
    ],
    install_requires=[
        'h5py',
        'healpy!=1.12.0',  # FIXME: https://github.com/healpy/healpy/pull/457
        'lalsuite',
        'ligo-gracedb>=2.2.0',
        'ligo-segments',
        'ligo.skymap>=0.1.1',
        'lscsoft-glue',
        'lxml',
        'numpy>=1.14.5',
        #'pycbc-pylal',
        'scipy>=0.7.2',
        'voeventlib>=1.2'
    ],
    python_requires='>=3.6',
)

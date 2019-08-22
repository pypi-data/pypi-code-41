#!/usr/bin/env python3
# rstwatch setup script

import os
from setuptools import setup
import unittest

# Set __version__ without importing anything
this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, 'rstwatch', 'version.py')) as f:
    exec(f.read())


def readme(filename):
    with open(filename) as f:
        return f.read()


def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='rstwatch',
    version=__version__,
    description="Watch directories for changes to RST files and generate HTML",
    long_description=readme('README.rst'),
    license='BSD-2-Clause',
    author='David Handy',
    author_email='cpif@handysoftware.com',
    url='https://bitbucket.org/dhandy2013/rstwatch',
    download_url='https://bitbucket.org/dhandy2013/rstwatch/get/tip.zip',
    packages=['rstwatch'],
    entry_points={
        'console_scripts': ['rstwatch=rstwatch.__main__:main'],
    },
    install_requires=['docopt>=0.5.0', 'docutils>=0.13'],
    test_suite='setup.get_test_suite',
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
)

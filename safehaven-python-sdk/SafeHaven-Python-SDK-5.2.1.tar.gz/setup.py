#!/usr/bin/env python
#
# Installer Script for SafeHaven Python SDK
#
import re
import glob
import sys
from setuptools import setup, find_packages

# Read in version file
execfile('dgpy/version.py')

setup(
    name="SafeHaven-Python-SDK",
    description='SafeHaven Python SDK (GRPC API)',
    long_description='SafeHaven Python SDK with example programs in dgpy/test_commands',
    keywords="SafeHaven DRaaS CAM AWS CLC Azure",
    classifiers=[ # See https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
    install_requires=['grpcio', 'grpcio-tools', 'PyYAML'],
    packages=find_packages(),
    package_data={
        'dgpy': ['test_commands/*.py', 'test_commands/example_configurations/*'],
    },
    license="MIT",
    zip_safe=True,

    # The following fields are similar to the information in the .deb package:
    version=__version__, # Set in version file
    author='Shi Jin',
    author_email='Shi.Jin@ctl.io',
    url='https://ca.ctl.io/cloud-application-manager',
)

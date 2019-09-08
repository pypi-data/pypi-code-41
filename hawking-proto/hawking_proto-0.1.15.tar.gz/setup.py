#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import sys
from setuptools import setup

platform = sys.platform
print(platform)

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['grpcio>=1.22.0', 'protobuf>=3.9.0']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="Peach Inc",
    author_email='hi@peach.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
    ],
    description="This package contains Hawking Proto messages and gRPC stubs definitions",
    install_requires=requirements,
    keywords='hawking_proto',
    name='hawking_proto',
    packages=['hawking_proto'],
    include_package_data=True,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://www.peach.co',
    version='0.1.15',
    zip_safe=False,
    license='Apache License, Version 2.0'
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

import clickntrack

project_dir = os.path.dirname(os.path.realpath(__file__))
requirement_file_path = project_dir + '/requirements.txt'
requirements = []
if os.path.isfile(requirement_file_path):
    with open(requirement_file_path) as f:
        requirements = f.read().splitlines()

setup(
    name=clickntrack.__name__,
    version=clickntrack.__version__,
    author=clickntrack.__author__,
    author_email=clickntrack.__author_email__,
    url='https://bitbucket.org/clickntrack/clickntrack-backend',
    description='Click & Track services - REST API for short URL handling',
    long_description=open('README.rst').read(),
    license="Apache License, Version 2.0",

    packages=find_packages(exclude=['tools']),
    include_package_data=True,
    install_requires=requirements,

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers'
    ],
    keywords='URL shortener'
)

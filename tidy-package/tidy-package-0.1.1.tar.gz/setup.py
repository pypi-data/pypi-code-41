#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

setup(
    name="tidy-package",
    version="0.1.1",
    author="gy",
    author_email="ganyu_private@gmail.com",
    description="python package test",
    long_description=open("README.md").read(),
    license="MIT",
    url="https://github.com/TechOpsX/tidypackage",
    packages=['tidy'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ],
)

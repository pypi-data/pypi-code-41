#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='abode',
    version='0.1.4',
    description='Python Environment and Package Manager',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Mat Leonard',
    author_email='leonard.mat@gmail.com',
    url='https://github.com/mcleonard/abode',
    packages=['abode'],
    scripts=['cli/abode'],
    install_requires=[
        'pyyaml',
    ]
    )
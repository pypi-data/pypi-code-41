#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

# read in the contents of README file
with open("README.md", "r") as f:
    long_description = f.read()

# package metadata
setup(
    author='Gabby Shvartsman',
    author_email='gabbyshvartsman@berkeley.edu',
    description='Single-Unit Electrode DEcoding',
    long_description=long_description.strip('\n'),
    long_description_content_type='text/markdown',
    name='suede',
    url='https://github.com/czbiohub/suede',
    python_requires='>=3.6.0',
    packages=['suede'],
    version='0.1.0'
)

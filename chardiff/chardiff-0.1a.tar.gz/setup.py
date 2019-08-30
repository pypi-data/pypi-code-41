#!/usr/bin/env python

from distutils.core import setup

setup(
    name='chardiff',
    version='0.1a',
    description='Compare 2 strings and highlight differences',
    long_description=open("README.md").read(),
    author='Matt Copperwaite',
    author_email='matt@copperwaite.net',
    url='https://github.com/yamatt/python3-chardiff',
    packages=['chardiff'],
    scripts=['scripts/chardiff']
)

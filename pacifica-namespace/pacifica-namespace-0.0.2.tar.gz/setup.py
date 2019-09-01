#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the pacifica service."""
from os import path
from setuptools import setup, find_packages

setup(
    name='pacifica-namespace',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Namespace Package',
    url='https://github.com/pacifica/pacifica-namespace/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='dmlb2000@gmail.com',
    packages=find_packages()
)

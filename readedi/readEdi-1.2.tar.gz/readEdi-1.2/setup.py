#!/usr/bin/python
# -*- coding: utf-8 -*-

import setuptools
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()

setuptools.setup(
    name='readEdi',
    version='1.2',
    description='Two-way fixed-width <--> Python dict converter.',
    long_description = README_TEXT,
    long_description_content_type='text/markdown',
    author='Elison Márcio Correa',
    author_email='marcioinfo.correa@gmail.com',
    url='https://github.com/marcioinfo/PositionalFilesReader',
    install_requires=['six'],
    license='BSD',
    keywords='Edi Parse',
    test_suite="readEdi.tests",
    classifiers=[],
)

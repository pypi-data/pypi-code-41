#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'AJay'
__mtime__ = '2019/8/29 0029'

"""

from setuptools import setup, find_packages

# with open("README.md", "r",encoding='GBK') as fh:
#     long_description = fh.read()

setup(
    name='HubbleSec',
    version='1.0',
    description='python library for Guanxing',
    author='AJay13',
    author_email='1599121712@qq.com',
    url='https://github.com/Hatcat123/HubbleSec',
    # long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['hubblesec.hubblerun'],
    # packages=['demo3','demo2.config'],
    packages=find_packages(),
    install_requires =[
        'requests',
        'flask'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

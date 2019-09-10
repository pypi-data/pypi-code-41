#! /usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
File name: setup.py
Version: 0.1
Author: Priyanshu Jain <priyanshu@pm.me>
Helpful decorators + utils for choice fields for finance related terms like currency pair, fx transaction types etc.
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
f = path.join(here, 'README.md')

long_description = """
Helpful decorators + utils for choice fields for finance related terms like currency pair, fx transaction types etc.
"""
setup(
    name='fin-choices-utils',
    version='1.0.1',
    description=(
        "A helpful decorator for choice fields"
        " (Django choices or SQLAlchemy ChoiceType)"),
    long_description=long_description,
    url='https://github.com/spotlight-co/fin-choices-utils',
    author='Priyanshu Jain',
    author_email='priyanshu@pm.me',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='django orm sqlalchemy choices',
    packages=find_packages(),
    py_modules=['orm_choices'],
    entry_points='''''',
    install_requires=[],
    extras_require={
        'dev': [''],
        'test': [''],
    },
)

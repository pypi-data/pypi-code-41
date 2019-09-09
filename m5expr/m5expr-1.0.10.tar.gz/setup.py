#!/usr/bin/env python3

import setuptools

from m5expr import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()
from m5expr import __version__

setuptools.setup(
    name = 'm5expr',
    version = __version__,
    author = 'Eric Smith',
    author_email = 'spacewar@gmail.com',
    description = 'A simple arithmetic expression parser and evaluator',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/brouhaha/m5expr',
    py_modules = ['m5expr'],
    install_requires = ['pyparsing'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Interpreters',
    ],
    python_requires='>=3.7',
)

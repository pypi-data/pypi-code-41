#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://sudokumizer.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='sudokumizer',
    version='0.0.3',
    description='The board() method returns a Sudoku board sollution. Use as a starting point for your own Sudoku creations.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Tomas Forsman',
    author_email='tomas@forsman.dev',
    url='https://github.com/tomasforsman/sudokumizer',
    packages=[
        'sudokumizer',
    ],
    package_dir={'sudokumizer': 'sudokumizer'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords='sudokumizer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

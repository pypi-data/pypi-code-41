#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from glob import glob
import os

from setuptools import find_packages
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setup(
    name='pylibversion',
    version='0.1.0',
    license='Apache License, Version 2.0',
    description='A library to help manage python library versions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='David Bradford',
    author_email='david.bradford@mongodb.com',
    url='https://github.com/dbradf/pylibversion',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=[
        'requests ~= 2.0',
    ],
)

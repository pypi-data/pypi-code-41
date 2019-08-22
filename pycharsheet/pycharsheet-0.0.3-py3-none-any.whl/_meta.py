#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger <taywee@gmx.com> and Brandon Phillips
# This code is released under the license described in the LICENSE file

from packaging.version import Version

version = Version('0.0.3')

data = dict(
    name='pycharsheet',
    version=str(version),
    author='Taylor C. Richberger and Brandon Phillips',
    description='A library and utility for managing a role playing game character sheet and some character state as well',
    license='MIT',
    keywords='dnd dungeons dragons rpg game utility',
    url='https://gitlab.com/Taywee/pycharsheet',
    entry_points=dict(
        console_scripts=(
            'pycharsheet = pycharsheet.__main__:main',
        ),
    ),
    packages=(
        'pycharsheet',
    ),
    install_requires=(
        'setuptools == 41.0.1',
        'lupa == 1.8',
    ),
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Role-Playing',
    ),
)

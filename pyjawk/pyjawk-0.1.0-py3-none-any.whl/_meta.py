# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger and Brandon Phillips
# This code is released under the license described in the LICENSE file

from packaging.version import Version

version = Version('0.1.0')

data = dict(
    name='pyjawk',
    version=str(version),
    author='Taylor C. Richberger',
    description='A Python-based stream editor for json documents',
    license='MIT',
    keywords='utility',
    url='https://gitlab.com/Taywee/pyjawk',
    entry_points=dict(
        console_scripts=(
            'pyjawk = pyjawk.__main__:main',
        ),
    ),
    packages=(
        'pyjawk',
    ),
    install_requires=(
        'packaging == 19.1',
        'ptpython == 2.0.4',
        'appdirs == 1.4.3',
    ),
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ),
)

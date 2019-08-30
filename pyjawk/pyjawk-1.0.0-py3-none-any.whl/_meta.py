# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger and Brandon Phillips
# This code is released under the license described in the LICENSE file

from packaging.version import Version

version = Version('1.0.0')

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
            'pyyawk = pyjawk.__main__:pyyawk',
            'pyxawk = pyjawk.__main__:pyxawk',
            'pymawk = pyjawk.__main__:pymawk',
            'pypawk = pyjawk.__main__:pypawk',
            'pysawk = pyjawk.__main__:pysawk',
            'pybawk = pyjawk.__main__:pybawk',
        ),
    ),
    packages=(
        'pyjawk',
    ),
    install_requires=(
        'packaging',
        'ptpython',
        'appdirs',
        'PyYAML',
        'msgpack',
    ),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ),
)

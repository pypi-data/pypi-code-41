#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='pypldl',
    version='2.0.0',

    description='A crawler with parallel downloading',
    url=None,
    author='Benoît Ryder',
    author_email='benoit@ryder.fr',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    packages=find_packages(),
    install_requires=['beautifulsoup4', 'urllib3', 'html5lib'],

    entry_points={
        'console_scripts': [
            'pypldl=pypldl.cli:main',
        ],
        'gui_scripts': [
            'pypldl-gui=pypldl.gui:main'
        ],
    },
)

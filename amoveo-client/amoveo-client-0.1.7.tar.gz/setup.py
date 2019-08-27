#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='amoveo-client',
    version='0.1.7',
    description='amoveo python client',
    long_description_markdown_filename='README.md',
    author='Dmitry Zhidkih',
    author_email='zhidkih.dmitry@gmail.com',
    url='https://github.com/dmitry1981/amoveo-client',
    include_package_data=True,
    install_requires=[
        'requests',
        'fastecdsa==1.6.5',
        'ecdsa==0.13',
    ],
    # setup_requires=['setuptools-markdown'],
    python_requires='>=3.6,<4',
    extras_require={},
    py_modules=['amoveo', ],
    license="MIT",
    zip_safe=False,
    keywords='amoveo veo',
    packages=find_packages(exclude=['docs', 'tests']),
)

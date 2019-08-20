#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["PyYAML>=5.1.1"]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Frank Xu",
    author_email='frank@frankxu.me',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent",
    ],
    description="FX's personal common lib",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fx_lib',
    name='fx_lib',
    packages=find_packages(include=['fx_lib']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/frankyxhl/py_fx_lib',
    version='0.1.5',
    zip_safe=False,
)

# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'pycryptodome',
    'requests',
]

setup(
    name='nezha',
    version='0.0.20',
    description="nezha, pysuway's utils",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True
)

# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = [
]

setup(
    name='flask_mongo_auth',
    version='0.0.2',
    author='kougazhang',
    author_email='kougazhang@gmail.com',
    url='https://github.com/kougazhang',
    description="flask authentication used mongodb stored",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
)


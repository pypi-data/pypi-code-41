#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='human_security',
      version='0.4',
      description='A library for making encryption/decryption easier',
      author='Massimo DiPierro',
      author_email='massimo.dipierro@gmail.com',
      long_description='',
      url='https://github.com/mdipierro/human_security',
      install_requires=['cryptography'],
      py_modules=["human_security"],
      license= 'BSD',
      package_data = {'': ['README.md']},
      keywords='human_security',
      )

#!/usr/bin/env python

from setuptools import setup

setup(
    name='ariadne-extensions',
    version='0.1.1',
    url='https://github.com/aleszoulek/ariadne-extensions',
    author='Ales Zoulek',
    author_email='ales.zoulek@gmail.com',
    packages=['ariadne_extensions'],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    install_requires=[
    ],
)

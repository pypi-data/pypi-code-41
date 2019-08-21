#!/usr/bin/env python
from setuptools import setup, find_packages

requires = ['Sphinx>=0.6',
        ]

setup(
    name='sphinxcontrib-cmd2img',
    version='0.2',
    url='https://github.com/stathissideris/sphinxcontrib-cmd2img',
    license='BSD',
    author='Yongping Guo',
    author_email='guoyoooping@163.com',
    description='Sphinx extension to render the image by script or command',
    long_description=open('README.rst').read(),
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)

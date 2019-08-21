#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='lendable-parsing-tool',
    version='1.0.0',
    description='Landable parsing tool',
    author='Omar Diaz',
    author_email='omar.diaz@crosslend.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'pony',
      'Click',
      'mysqlclient',
      'dsnparse',
      'beautifulsoup4',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'lendable_parse_tool=landable_parse_tool:tool',
        ]
    },
)

#!/usr/bin/env python3

from setuptools import setup

setup(name='tap-impactradius',
      version='0.1.0',
      description='Singer.io tap for extracting data from api.impactradius.com',
      author='Onedox',
      url='https://github.com/onedox/tap-impactradius',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_impactradius'],
      install_requires=[
          'requests>=2.13.0',
          'singer-python>=1.4.2',
      ],
      entry_points='''
          [console_scripts]
          tap-impactradius=tap_impactradius:main
      ''',
      packages=['tap_impactradius'],
      package_data = {
          'tap_rimpactradius/schemas': [
              "clicks.json",
              "actions.json",
              "invoices.json",
          ],
      },
      include_package_data=True,
)

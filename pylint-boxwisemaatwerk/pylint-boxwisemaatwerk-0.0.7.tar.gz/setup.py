# -*- coding: UTF-8 -*-
"""
Setup module for Pylint plugin for boxwise maatwerk.
"""
from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read() + "\n" + open('CHANGELOG.md').read()

setup(
    name='pylint-boxwisemaatwerk',
    url='https://bitbucket.org/tranconbv/pylint-boxwisemaatwerk',
    author='Kevin Pawiroredjo, Ana Caires',
    author_email='k.pawiroredjo@trancon.nl',
    description='A Pylint plugin to help Pylint understand the boxwise maatwerk framework',
    long_description=LONG_DESCRIPTION,
    version='0.0.7',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pylint>=1.9.4', 'pylint-plugin-utils>=0.5'
    ],
    extras_require={
        'for_tests': ['coverage', 'pytest'],
    },
    license='CLOSED',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Topic :: Software Development :: Quality Assurance',
        'Programming Language :: Python :: 2.7'
    ],
    keywords=['pylint', 'boxwise', 'plugin'],
    zip_safe=False,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = []

if sys.version_info.major == 2:
    requirements.append('django<2')
else:
    requirements.append('django')

test_requirements = [
    'django-nose>=1.2',
    'factory_boy>=2.4,<3.0',
    'fake-factory>=0.4.0,<1',
    'nosexcover>=1.0.8, <2',
    'ipdb',
    'mock',
    'wheel',
    'coveralls'
]

setup(
    name='django2_manager_cache',
    version='1.0.1',
    description='Manager to Cache Django Models',
    long_description=readme + '\n\n' + history,
    author='Gabriel Omar Masi (rayser)',
    url='https://github.com/gabomasi/django2_manager_cache',
    packages=find_packages(exclude=('tests',)),
    package_dir={'django2_manager_cache':
                 'django2_manager_cache'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='django2_manager_cache',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6'
    ],
    test_suite='nose.collector',
    tests_require=test_requirements,
)

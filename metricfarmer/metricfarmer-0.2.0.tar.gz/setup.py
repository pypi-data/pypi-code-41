#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

requires = ['click', 'colorama', 'requests']

setup(
    name='metricfarmer',
    version='0.2.0',
    url='http://github.com/useblocks/metricfarmer',
    download_url='http://pypi.python.org/pypi/metricfarmer',
    license='MIT',
    author='team useblocks',
    author_email='info@useblocks.com',
    description='Collects and stores metrics for your project.',
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points={
        'console_scripts': ['metricfarmer = metricfarmer:mf_cli'],
        'metricfarmer': ['metricfarmer_basics=metricfarmer.extensions:MF']
    }
)

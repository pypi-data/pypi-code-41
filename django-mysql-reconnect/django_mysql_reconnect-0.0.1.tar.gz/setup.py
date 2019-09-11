#!/usr/bin/env python
from __future__ import with_statement, print_function

from setuptools import setup, find_packages

setup(
    name='django_mysql_reconnect',
    version='0.0.1',
    author='jiaojiao',
    author_email='jiaojiaox.zhao@intel.com',
    packages=['django_mysql_reconnect'],
    description='DjangoDatabaseReconnect',
    url='',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)

# encoding: utf-8
################################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Setup script.
"""

from setuptools import find_packages
import setuptools

from duedge_cli import _VERSION_

with open("README.rst", "r") as ld:
    long_description = ld.read()

setuptools.setup(
    name='duedge-cli',
    url='https://duedge.baidu.com',
    version=_VERSION_,
    author='xuyanfei, likewei',
    author_email='likewei@baidu.com',
    description='duedge command line tool',
    long_description=long_description,
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.10.0',
        'fire>=0.1.3',
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
    package_data={
        'duedge_cli': ['doc/system/*.txt', 'doc/trigger/*.txt', 'doc/function/*.txt'],
    },
    data_files=[
        ('duedge_cli', ['duedge_cli/.sysconfig']),
        ('duedge_cli/doc', ['duedge_cli/doc/overview.txt']),
    ],
    entry_points={
        'console_scripts': [
            'duedge = duedge_cli.__main__:main',
        ]
    },
    scripts=['bin/duedge'],
)
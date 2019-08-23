#!/usr/bin/env python
"""Distutils installer for rabbitfixture."""

from setuptools import setup, find_packages


install_requires = [
    'amqp >= 2.0.0',
    'fixtures >= 0.3.6',
    'setuptools',
    'subprocess32; python_version < "3"',
    'testtools >= 0.9.12',
    ]

setup(
    name='rabbitfixture',
    version="0.4.2",
    packages=find_packages('.'),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    description='Magic.',
    install_requires=install_requires,
    extras_require={
        'test': [
            'six',
            ],
        })

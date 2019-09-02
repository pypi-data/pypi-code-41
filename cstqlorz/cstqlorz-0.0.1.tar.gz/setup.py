#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='cstqlorz',
    version='0.0.1',
    author='IcedOtaku',
    author_email='i@waitforaday.site',
    url='https://waitforaday.site',
    description=u'陈少太强辣',
    packages=['cstqlorz'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cstql=cstqlorz:cstql',
            'wtcl=cstqlorz:wtcl'
        ]
    }
)
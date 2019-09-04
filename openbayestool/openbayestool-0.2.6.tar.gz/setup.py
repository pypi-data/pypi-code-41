# -*- coding: utf-8 -*-

import importlib
import os
from setuptools import setup


version = importlib.import_module(
    'openbayestool.version', os.path.join('openbayestool', 'version.py')).VERSION

setup(
    name='openbayestool',
    version=version,
    packages=['openbayestool'],
    install_requires=[
        'requests>=2.17.3'
    ],
    zip_safe=False,
    author='Openbayes',
    description='Openbayes Service Tool',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ml ai openbayes',
    url='https://openbayes.com'
)

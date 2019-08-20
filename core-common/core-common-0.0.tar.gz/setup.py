#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

version, license = None, None
with open('common/__init__.py', 'r') as fd:
    content = fd.read()
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)
    license = re.search(r'^__license__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)
if version is None: raise RuntimeError('Cannot find version information')
if license is None: raise RuntimeError('Cannot find license information')

with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
    name='core-common',
    version=version,
    description='Research CORE ERM - common module',
    author='Ricardo Ribeiro, Hugo Cachitas',
    author_email='ricardojvr@gmail.com, hugo.cachitas@research.fchampalimaud.org',
    url='https://github.com/research-core/core-common',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    license=license,
    install_requires=['pyforms-web', 'notifications-central']
)

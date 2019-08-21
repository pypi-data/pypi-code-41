#!/usr/bin/env python
# Copyright (c) 2017 Radware LTD. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
import os
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='vdirect_client',
      version='4.9.0-4',
      description='Radware vDirect server python REST client',
      long_description = readme(),
      classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python'
      ],
      keywords="radware vdirect python REST client",
      url='https://pypi.python.org/pypi/vdirect_client',
      author='Avishay Balderman',
      author_email='avishayb@radware.com',
      packages=['vdirect_client'],
	  license='ASL 2.0',
      zip_safe=False)

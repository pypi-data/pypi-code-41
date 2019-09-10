# Copyright (C) 2019 Erhu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The setup.py file for Python Dkrs."""

from setuptools import setup, find_packages

LONG_DESCRIPTION = """
Python Dkrs is a library contains some useful toolkit.
""".strip()

SHORT_DESCRIPTION = """
A library to simplify Git/File/Network operations.""".strip()

DEPENDENCIES = [
    'requests',
]

TEST_DEPENDENCIES = [
]

VERSION = '0.1.0'
URL = 'https://github.com/erhu/dkrs'

setup(
    name='dkrs',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,

    author='Erhu',
    author_email='erhu.cn@gmail.com',
    license='Apache Software License',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
    ],

    keywords='git network requests system',

    packages=find_packages(),

    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
)

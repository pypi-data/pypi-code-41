# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup script."""
from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup
import time

long_description = '''
FIXME
'''

version = "0.0.1"
stub = str(int(time.time()))  # Used to increase version automagically.
version = version + '.' + stub

setup(
    name="scaaml",
    version=version,
    description="Side Channel Attack Assisted with Machine Learning",
    long_description=long_description,
    author='Elie Bursztein',
    author_email='scaaml@google.com',
    url='https://github.com/google/scaaml',
    license='Apache License 2.0',
    install_requires=[
        'colorama',
        'termcolor',
        'tqdm',
        'pandas',
        'numpy',
        'tabulate',
        'h5py',
        'matplotlib',
        'Pillow'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: Jupyter',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    packages=find_packages()
)

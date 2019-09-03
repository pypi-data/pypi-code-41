"""
 Copyright 2019 The Kathra Authors.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 Contributors:

    IRT SystemX (https://www.kathra.org/)    

"""

# coding: utf-8

from setuptools import setup, find_packages

NAME = "kathra-core-interface"
VERSION = "1.0.1"

# To install the library, run the following
#
# python setup.py install
# or
# pip install . (after cd to this folder)
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    'connexion == 1.1.9',
    'python_dateutil == 2.6.0',
    'kathra-core-model == 1.0.1'
]

setup(
    name=NAME,
    version=VERSION,
    description="Kathra Core Interface",
    author="Julien Boubechtoula",
    author_email="julien.boubechtoula@gmail.com",
    url="https://gitlab.com/kathra/kathra-staging/kathra/kathra-core/kathra-core-python/kathra-core-interface",
    keywords=["Interface","Core", "Kathra"],
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Core modules for python interface in Kathra
    """,
    long_description_content_type="text/plain",
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)


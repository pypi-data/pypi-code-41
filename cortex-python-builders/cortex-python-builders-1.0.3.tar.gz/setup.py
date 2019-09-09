"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup
from setuptools import find_packages

with open('README.md') as f:
    long_description = f.read()

setup(name='cortex-python-builders',
      description="Support for programmatic creation of resources in the CognitiveScale Cortex Cognitive Platform",
      long_description=long_description,
      long_description_content_type='text/markdown',
      version='1.0.3',
      author='CognitiveScale',
      author_email='info@cognitivescale.com',
      url='https://github.com/CognitiveScale/cortex-python-builders',
      license='Apache License Version 2.0',
      platforms=['linux', 'osx'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'cortex-python>=1.0.1',
          'cuid>=0.3,<1',
          'dill>=0.2.8.2',
          'pyjwt>=1.6.1,<2',
          'jinja2',
          'docker>=3.7.2',
          'tenacity>=5.0.2',
          'dataclasses>=0.6; python_version == "3.6"',
          'more_itertools>=4.3.0,<5'
      ],
      tests_require=[
          'mocket>=2.5.0,<3',
          'mock>=2,<3',
          'scikit-learn>=0.20.0,<1',
          'pytest>=3.2.5,<4',
          'pandas>=0.24',
          'numpy>=1.16',
          'pipdeptree'
      ],
      classifiers=[
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.6',
      ])

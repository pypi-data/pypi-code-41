# Copyright 2019 S. Pawar, S. Semper
#     https://www.tu-ilmenau.de/it-ems/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Usage:
# Docu: python setup.py build_sphinx -E
# Test: python setup.py test

from setuptools import setup
from eadf import __version__
from sphinx.setup_command import BuildDoc
cmdclass = {'build_sphinx': BuildDoc}

name = 'eadf'
author = 'S. Pawar, S. Semper'
group = ', EMS Group, TU Ilmenau, 2019'
release = '0.2'

setup(
    author=author,
    version=__version__,
    name=name,
    packages=[name],
    author_email='sebastian.semper@tu-ilmenau.de',
    description='Effective Aperture Distribution Function',
    url='https://eadf.readthedocs.io/en/latest/',
    license='Apache Software License',
    keywords='signal processing',
    test_suite="test",
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
    ],
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'copyright': ('setup.py', author + group),
            'version': ('setup.py', __version__),
            'release': ('setup.py', __version__),
            'source_dir': ('setup.py', 'doc/source'),
            'build_dir': ('setup.py', 'doc/build'),
        }
    },
)

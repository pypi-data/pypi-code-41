#!/usr/bin/env python3

from __future__ import absolute_import


import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='monicacrm',
    version='0.1.0',
    description='A client library for the MonicaHQ.com personal relationships manager to assist with tasks like bulk import.',
    author='Cathal Garvey',
    author_email='cathalgarvey@cathalgarvey.me',
    url='https://gitlab.com/cathalgarvey/python-monicacrm',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Issue Tracker': 'https://gitlab.com/cathalgarvey/python-monicacrm/issues',
    },
    keywords=[
        'monica', 'monicahq', 'crm', 'relationships', 'assistive technology'
    ],
    python_requires='>=3.6, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        'click',
        'requests',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    setup_requires=[
    ],
    entry_points={
        'console_scripts': [
            'monicacrm = monicacrm.cli:main',
        ]
    },
)

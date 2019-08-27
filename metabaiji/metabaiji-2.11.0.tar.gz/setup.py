from __future__ import print_function
# https://coderwall.com/p/qawuyq
# Thanks James.

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''
    print('warning: pandoc or pypandoc does not seem to be installed; using empty long_description')

import os
requirements_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'requirements.txt')
with open(requirements_file, 'r') as f:
    install_requires = [x.strip() for x in f.readlines()]

import importlib
from setuptools import setup

setup(
    name='metabaiji',
    version=importlib.import_module('baiji.package_version').__version__,
    author='Body Labs',
    author_email='github@paulmelnikow.com',
    description='High-level Python abstraction layer for Amazon S3',
    long_description=long_description,
    url='https://github.com/metabolize/baiji',
    license='MIT',
    packages=[
        'baiji',
        'baiji/util',
    ],
    scripts=[
        'bin/s3',
    ],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

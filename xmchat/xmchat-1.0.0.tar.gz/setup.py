#!/usr/bin/env python
import os
import re

import setuptools

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `__init__.py`.
    """
    path = os.path.join(os.path.dirname(__file__), package, '__init__.py')
    with open(path, 'rb') as f:
        init_py = f.read().decode('utf-8')
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setuptools.setup(
    name='xmchat',
    author='Haoming Wang',
    version=get_version('xmchat'),
    license='Apache 2.0',
    url='https://github.com/haomingw/xmchat',
    description='Library for building powerful interactive chatbot in Python',
    long_description=long_description,
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)

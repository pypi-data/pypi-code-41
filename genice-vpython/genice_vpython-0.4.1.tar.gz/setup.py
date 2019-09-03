#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, Extension
from numpy.distutils.misc_util import get_numpy_include_dirs
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(os.path.dirname(__file__), 'genice_vpython', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))
    
long_desc = "".join(open("README.md").readlines())

setup(
    name='genice_vpython',
    version=metadata['version'],
    description='VPYTHON format plugin for GenIce.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ],
    author='Masakazu Matsumoto',
    author_email='vitroid@gmail.com',
    url='https://github.com/vitroid/genice-vpython/',
    keywords=['genice', 'VPYTHON'],

    packages=['genice_vpython',
              'genice_vpython.formats',
    ],
    
    entry_points = {
        'genice_format': [
            'vpython      = genice_vpython.formats.vpython',
        ],
    },
    install_requires=['vpython', 'genice>=0.25'],

    license='MIT',
)

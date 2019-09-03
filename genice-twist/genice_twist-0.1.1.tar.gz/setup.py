#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, Extension
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(os.path.dirname(__file__), 'genice_twist', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))
    
long_desc = "".join(open("README.md").readlines())


setup(
    name='genice_twist',
    version=metadata['version'],
    description='Twist analysis plugin for GenIce.',
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
    url='https://github.com/vitroid/genice-twist/',
    keywords=['genice', 'chirality'],

    packages=['genice_twist',
              'genice_twist.formats',
    ],
    
    entry_points = {
        'genice_format': [
            'twist  = genice_twist.formats.twist',
        ],
    },
    install_requires=['genice>=0.25', 'genice-svg>=0.4', 'twist-op>=0.2'],

    license='MIT',
)

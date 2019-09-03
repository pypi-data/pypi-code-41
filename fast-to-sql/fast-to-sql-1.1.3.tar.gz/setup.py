# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 10:03:10 2018

@author: jglasej
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.dirname(__file__)

# Get the long description from the README file
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='fast-to-sql',
    version='1.1.3',
    description='An improved way of uploading pandas DataFrames to MS SQL server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jdglaser/fast_to_SQL',
    author=['Jarred Glaser'],
    author_email='jarred.glaser@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
        ],
    install_requires=["pandas", "sqlalchemy", 'datetime'],
    keywords='pandas to_sql fast sql',
    packages=['fast_to_SQL'],
)

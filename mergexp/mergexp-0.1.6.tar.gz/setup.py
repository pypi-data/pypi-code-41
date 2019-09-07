#!/usr/bin/env python
import os
import io
from setuptools import find_packages, setup

NAME = 'mergexp'
DESCRIPTION = 'Python Merge Experimentation Library'
URL = 'https://gitlab.com/mergetb/xir/tree/master/lang/mx'
EMAIL = 'rgoodfel@isi.edu'
AUTHOR = 'Ryan Goodfellow'
REQUIRES_PYTHON = '>=3'
VERSION = "v0.1.6"
REQUIRED = []

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, 'README.md')) as f:
    LDESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    long_description=LDESCRIPTION,
    long_description_content_type="text/markdown",
    license='Apache2.0',
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

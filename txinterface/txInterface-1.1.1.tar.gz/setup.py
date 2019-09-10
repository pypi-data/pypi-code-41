#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="txInterface",
    version="1.1.1",
    author="liudx",
    author_email="messliu@163.com",
    description="Tx Interface Automated Testing",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/messliu/autotest.git",
    packages=['txInterface'],
    classifiers=[
        'Development Status :: 4 - Beta',
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Multimedia :: Video',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)




#!/usr/bin/env python3
import setuptools
import os

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simplebrainviewer",
    version='0.1',
    author="Andrew Van",
    author_email="vanandrew@wustl.edu",
    description="A simple brain viewer using matplotlib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vanandrew/SimpleBrainViewer",
    packages=setuptools.find_packages(),
    install_requires=[
        'nibabel',
        'matplotlib',
    ],
    scripts=['sbv'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)

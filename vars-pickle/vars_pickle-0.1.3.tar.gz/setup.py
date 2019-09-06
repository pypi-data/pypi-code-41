# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 14:45:27 2019

@author: 10167232
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vars_pickle",
    version="0.1.3",
    author="karond",
    author_email="dingyaohui.g@outlook.com",
    description="Save your variable as Rstudio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires = ['pandas','numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
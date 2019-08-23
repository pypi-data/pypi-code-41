#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang @ 2019-02-18 15:41:36

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-yunpian-app",
    version="1.0.3",
    author="Xiang Wang",
    author_email="ramwin@qq.com",
    description="用于云片网的django app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ramwin/django-yunpian-app",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "yunpian-python-sdk"
    ],
)

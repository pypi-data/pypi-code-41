#!/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biggerquery",
    version="0.3.dev1",
    author=u"Chi",
    author_email="chibox-team@allegrogroup.com",
    description="BigQuery client wrapper with clean API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/allegro/biggerquery",
    packages=["biggerquery"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "google-cloud-bigquery>=1.12.0, <1.19.0",
        "pandas>=0.23.0, <0.24",
        "google-cloud-dataflow==2.5",
        "numpy>=1.14.0, <1.17",
        "google-cloud-storage==1.19.0",
    ]
)

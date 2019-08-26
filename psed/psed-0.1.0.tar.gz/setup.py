#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=7.0"]
test_requirements = [
    "pytest>=5.1.0",
    "pytest-cov>=2.7.0",
    "pyfakefs==3.6",
    "pytest-azurepipelines==0.8.0",
]
dev_requirements = ["tox==3.12.1", "black==19.3b0"]

setup(
    author="Andrzej Klajnert",
    author_email="py@aklajnert.pl",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="CLI utility for text search / replace.",
    entry_points={"console_scripts": ["psed=psed.__main__:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="psed",
    name="psed",
    packages=find_packages(include=["psed"]),
    test_suite="tests",
    extras_require={"test": test_requirements, "dev": dev_requirements},
    url="https://github.com/aklajnert/psed",
    version="0.1.0",
    zip_safe=False,
)

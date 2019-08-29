#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name="iso3_lookup",
    version="0.6.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["iso3_tests.py = iso3_lookup.tests.run"]},
    install_requires=["fuzzywuzzy", "python-Levenshtein"],
    author="Sam Watson",
    author_email="quadquants@gmail.com",
    description="Go from iso3 -> country name and visa versa",
    url="https://github.com/watson-sam/iso3_lookup",
)

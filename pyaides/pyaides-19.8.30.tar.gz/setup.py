#!/usr/bin/env python
import codecs
import os
import re

from setuptools import find_packages
from setuptools import setup


def meta(category, fpath="src/pyaides/__init__.py"):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, fpath), "r") as f:
        package_root_file = f.read()
    matched = re.search(
        r"^__{}__\s+=\s+['\"]([^'\"]*)['\"]".format(category), package_root_file, re.M
    )
    if matched:
        return matched.group(1)
    raise Exception("Meta info string for {} undefined".format(category))


requires = []

setup_requires = ["pytest-runner==4.4"]

test_requires = [
    "black==18.9b0",
    "coverage==4.5.2",
    "pre-commit==1.14.4",
    "pytest==4.2.1",
    "pytest-cov==2.6.1",
    "pytest-mock==1.10.4",
]

setup(
    name="pyaides",
    version=meta("version"),
    description="Light-weight Python 3 utilities",
    author=meta("author"),
    url="https://github.com/okomestudio/pyaides",
    platforms=["Linux"],
    classifiers=[],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.7",
    scripts=[],
    install_requires=requires,
    setup_requires=setup_requires,
    tests_require=test_requires,
    extras_require={"test": test_requires},
)

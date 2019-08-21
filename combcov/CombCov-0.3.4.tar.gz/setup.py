#!/usr/bin/env python

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="CombCov",
    version="0.3.4",
    author="Permuta Triangle",
    author_email="permutatriangle@gmail.com",
    description="Searching for combinatorial covers.",
    license="GPL-3",
    keywords="combinatorics covers automatic discovery",
    url="https://github.com/PermutaTriangle/CombCov",
    project_urls={
        "Source": "https://github.com/PermutaTriangle/CombCov",
        "Tracker": "https://github.com/PermutaTriangle/CombCov/issues",
    },
    packages=find_packages(),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=[
        "permuta==1.0.0",
        "PuLP==1.6.10",
    ],
    setup_requires=["pytest-runner==5.1"],
    tests_require=[
        "pytest==5.1.1",
        "pytest-cov==2.7.1",
        "pytest-pep8==1.0.6",
        "pytest-isort==0.3.1",
    ],
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",

        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)

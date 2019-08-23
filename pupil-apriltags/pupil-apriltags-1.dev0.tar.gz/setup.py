#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import platform
import shutil
from pathlib import Path

from skbuild import setup
from setuptools import find_packages
from setuptools.dist import Distribution

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["numpy"]

setup_requirements = ["scikit-build", "ninja", "pytest-runner"]

test_requirements = ["pytest"]


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(self):
        return True


source_folder = "src"
packages = find_packages(where=source_folder)
root_package = packages[0]

root_folder = Path(__file__).parent

clib_ext_by_platform = {"Darwin": "dylib", "Linux": "so", "Windows": "dll"}
clib_ext = clib_ext_by_platform[platform.system()]

cmake_args = []
if platform.system() == "Windows":
    cmake_args.append("-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=True")


setup(
    author="Pupil Labs GmbH",
    author_email="pypi@pupil-labs.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Python bindings for apriltags v3",
    # distclass=BinaryDistribution,
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="apriltags",
    name="pupil-apriltags",
    packages=packages,
    package_dir={"": "src"},
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/pupil-labs/apriltags",
    version="1.dev0",
    zip_safe=False,
    cmake_install_dir="src/pupil_apriltags",
    cmake_args=cmake_args,
)

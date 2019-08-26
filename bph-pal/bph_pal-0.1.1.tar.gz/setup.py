#!/usr/bin/env python3
# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""
    Setup file for riot_pal.
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


setup(
    name="bph_pal",
    version="0.1.1",
    author="Kevin Weiss",
    author_email="weiss.kevin604@gmail.com",
    license="MIT",
    description="Protocol abstraction and parser for BPH",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/riot-appstore/BPH",
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.4.*',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers"
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=['pyserial', 'wiringpi', 'smbus', 'deepdiff', 'readline'],
    entry_points={
        'console_scripts': ['bootload_philip=bph_pal.stm32uartboot:main',
                            'bph_shell=bph_pal.bph_shell:main'],
    }
)

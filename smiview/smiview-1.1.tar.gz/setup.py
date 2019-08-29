#!/usr/bin/env python

from setuptools import setup

DESCRIPTION = """\
smiview is a command-line, text-mode tool to show the structure of a
SMILES string.
"""

setup(
    name = "smiview",
    version = "1.1",
    description = DESCRIPTION,
    author = "Andrew Dalke",
    author_email = "dalke@dalkescientific.com",
    url = "https://bitbucket.org/dalke/smiview",
    license = "MIT",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    py_modules=["smiview"],
    entry_points = {
        "console_scripts": [
            "smiview=smiview:main",
            ],
        },

    )

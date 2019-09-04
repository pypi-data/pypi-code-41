#!/usr/bin/env python
from setuptools import setup

setup(
    name="jeera",
    version="0.2",
    description="CLI for jira for its dumb shenannigans",
    author="Chris Lee",
    author_email="chris@indico.io",
    packages=["jira"],
    install_requires=["requests>=2.22.0", "click>=7.0"],
    extras_require={"test": ["pytest"]},
    scripts=["bin/jira"],
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from __future__ import with_statement

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import ebr_trackerbot


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as changelog_file:
    changelog = changelog_file.read()

requirements = [
    "slackclient==2.1.0",
    "requests>=2.22.0,<3.0.0",
    "pendulum>=2.0.5,<3.0.0",
    "vault-anyconfig>=0.2.2,<0.3.0",
    "PyYAML>=5.1,<6",
]

extra_requirements = {"db_support": ["pyodbc>=4.0.27,<4.1.0"]}

setup_requirements = ["pytest-runner"] + extra_requirements["db_support"]

test_requirements = ["pytest", "pytest-cov", "coverage"]

setup(
    author=ebr_trackerbot.__author__,
    author_email=ebr_trackerbot.__email__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="EBR Tracker Slack Bot",
    entry_points={"console_scripts": ["ebr-trackerbot=ebr_trackerbot.cli:main"]},
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="ebr_trackerbot",
    name="ebr_trackerbot",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extra_requirements=extra_requirements,
    url="https://github.com/tomtom-international/ebr-trackerbot",
    version=ebr_trackerbot.__version__,
    zip_safe=False,
)

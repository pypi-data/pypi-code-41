#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from __future__ import with_statement

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import ebr_board


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as changelog_file:
    changelog = changelog_file.read()

requirements = [
    "ebr-connector>=0.1.4,<0.2",
    "Flask>=1.1.0,<2",
    "flask-restplus>=0.12.1,<0.13",
    "pendulum>=2.0.5,<3",
    "vault-anyconfig>=0.3.1,<0.4",
    "PyYAML>=5.1,<6",
]

extras_require = {"aws_lambda": ["aws-wsgi>=0.2.0", "ssm-parameter-store>=19.5.0,<20.0.0"]}

# Ensure that linting and testing will be done with all depedencies installed
collected_extras = []
for req_set in extras_require.values():
    collected_extras += req_set

setup_requirements = ["pytest-runner"] + collected_extras

test_requirements = ["pytest", "pytest-cov", "coverage"]

setup(
    author=ebr_board.__author__,
    author_email=ebr_board.__email__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="RESTful interface for Elastic Build Results.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="ebr_board",
    name="ebr_board",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extras_require=extras_require,
    url="https://github.com/tomtom-international/ebr-board",
    version=ebr_board.__version__,
    zip_safe=False,
)

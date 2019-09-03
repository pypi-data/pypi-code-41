# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
    Setup script to package Isogeo PySDK Python module

    see: https://github.com/isogeo/xml-toolbelt-py/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pathlib

from setuptools import find_packages, setup

# package (to get version)
from isogeo_xml_toolbelt.__about__ import __version__, __summary__

# SETUP ######################################################################

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# setup metadata
setup(
    # meta
    name="isogeo-xml-toolbelt",
    version=__version__,
    author="Isogeo",
    author_email="support@isogeo.com",
    description=__summary__,
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="GIS metadata INSPIRE Isogeo API REST geographical data ISO19139 XML geonetwork",
    license="LGPL3",
    url="https://github.com/isogeo/xml-toolbelt-py/",
    project_urls={
        "Docs": "https://isogeo-xml-toolbelt.readthedocs.io/",
        "Bug Reports": "https://github.com/isogeo/xml-toolbelt-py/issues/",
        "Source": "https://github.com/isogeo/xml-toolbelt-py/",
    },
    # dependencies
    install_requires=["lxml==4.4.*"],
    extras_require={
        "dev": ["black", "python-dotenv"],
        "test": ["codecov", "coverage", "pytest", "pytest-cov"],
    },
    python_requires=">=3.6, <4",
    # packaging
    packages=find_packages(
        exclude=["contrib", "docs", "*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

#!/usr/bin/env python3

from setuptools import setup, find_packages

NAME = "tkFilterList"
VERSION = "0.1.1"
AUTHOR = "Benjamin Johnson"
AUTHOR_EMAIL = "bmjcode@gmail.com"
DESCRIPTION = "Self-filtering Listbox with text entry for Tkinter"

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

URL = "https://github.com/bmjcode/tkFilterList"
PACKAGES = find_packages()
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      url=URL,
      packages=PACKAGES,
      classifiers=CLASSIFIERS)

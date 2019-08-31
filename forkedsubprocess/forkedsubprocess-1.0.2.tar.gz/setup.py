"""Forked Subprocess Support."""

import re
from setuptools import find_packages, setup

main_py = open('src/forkedsubprocess/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", main_py))

NAME = 'forkedsubprocess'
VERSION = metadata['version']

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name=NAME,
    version=VERSION,
    author="Nigel Kukard",
    author_email="nkukard@lbsd.net",
    description="Forked subprocess support for Python",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://gitlab.devlabs.linuxassist.net/allworldit/python/forkedsubprocess",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',

    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    package_data={'': ['LICENSE']}
)

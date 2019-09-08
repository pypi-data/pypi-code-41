"""Python BIRD client."""

import re
from setuptools import find_packages, setup

main_py = open('src/birdclient/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", main_py))

NAME = 'birdclient'
VERSION = metadata['version']

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name=NAME,
    version=VERSION,
    author="Nigel Kukard",
    author_email="nkukard@lbsd.net",
    description="Python BIRD client",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://gitlab.devlabs.linuxassist.net/allworldit/python/birdclient",
    classifiers=[
        "Development Status :: 3 - Alpha",
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

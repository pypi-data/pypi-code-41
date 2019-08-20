#!/usr/bin/env python
# -*- coding: utf-8 -*-
# based on template: https://github.com/kennethreitz/setup.py
import io
import os
import sys
import typing  # noqa
from shutil import rmtree

from setuptools import Command
from setuptools import find_packages
from setuptools import setup

import versioneer

# Package meta-data.
NAME = "csnake"
DESCRIPTION = "C code generation helper package."
URL = "https://gitlab.com/andrejr/csnake"
EMAIL = "r.andrej@gmail.com"
AUTHOR = "Andrej Radović"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = []  # type: typing.List[str]

# What packages are optional?
EXTRAS = {
    "numpy arrays/matrices/types as initializers": ["numpy"],
    "sympy arrays/matrices/types as initializers": ["sympy"],
    "pillow Images as initializers": ["pillow"],
}  # type: typing.Dict[str, typing.List[str]]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# # Load the package's __version__.py module as a dictionary.
# about = {}  # type: typing.Dict[str, typing.List[str]]
# if not VERSION:
#     with open(os.path.join(here, NAME, "__version__.py")) as f:
#         exec(f.read(), about)
# else:
#     about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []  # type:typing.List[str]

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(
            "{} setup.py sdist bdist_wheel --universal".format(sys.executable)
        )

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{}".format(versioneer.get_version()))
        os.system("git push --tags")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/x-rst; charset=UTF-8",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests", "benchmarks")),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
    # $ setup.py publish support.
    # cmdclass={"upload": UploadCommand},
)

import re

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = re.search('^__version__\s*=\s*"(.*)"', open("cognite/seismic/__init__.py").read(), re.M).group(1)

setuptools.setup(
    name="cognite-seismic-sdk",
    version=version,
    description="A wrapper for the Seismic Datastore API offered by Cognite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["cognite.seismic"],
    python_requires=">=3.6",
    license="Apache",
    author="Vegard Stikbakke",
    author_email="vegard.stikbakke@cognite.com",
    classifiers=["Development Status :: 3 - Alpha"],
)

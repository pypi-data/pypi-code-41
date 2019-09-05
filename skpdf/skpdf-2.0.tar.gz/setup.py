import setuptools
from pathlib import Path

setuptools.setup(
    name="skpdf",
    version=2.0,
    long_description="package by sk",
    packages=setuptools.find_packages(exclude=["test", "data"])
)

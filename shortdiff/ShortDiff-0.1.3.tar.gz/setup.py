#!/usr/bin/python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ShortDiff",
    version="0.1.3",
    author="Theo (Lattay) Cavignac",
    author_email="theo.cavignac@gmail.com",
    description="A simple one way diff tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lattay/ShortDiff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Information Technology",
    ],
)

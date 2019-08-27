#!usr/bin/env python

import setuptools

with open("README.md", "r") as readme_f:
    long_description = readme_f.read()

setuptools.setup(
    name="kvutil",
    version="1.0.2",
    author="mhv2109",
    description="Comand-line key-value store",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhv2109/kvutil",
    packages=["kvutil"],
    entry_points={
        "console_scripts": ["kv=kvutil:main", ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

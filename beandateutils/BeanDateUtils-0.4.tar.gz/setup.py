from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name="BeanDateUtils",
    version="0.4",
    author="Hly",
    author_email="hlyaction@gmail.com",
    description="A Python library for date compute.",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://github.com/beansKingdom/DateUtils",
    packages=find_packages(),
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

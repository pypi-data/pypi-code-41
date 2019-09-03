from __future__ import print_function
import os, sys
from setuptools import setup


VERSION = open('VERSION','r').read().strip()
print("assuming that the version is " + VERSION)

try:
   import pyscons
   docs = pyscons.__doc__
   print(docs, file=open("README.txt", "w"))
except:
   docs = open("README.txt", 'r').read()


setup(name="PyScons",
    version=VERSION,
    description="An extension to Scons which enables dependency tracking on python script imports.",
    long_description=docs,
    long_description_content_type="text/markdown",
    author="S. Joshua Swamidass",
    url="http://swami.wustl.edu/",
    author_email="swamidass@gmail.com",
    classifiers=["Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        "Intended Audience :: Developers",
        ],
    py_modules=['pyscons']
)

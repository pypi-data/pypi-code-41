# -*- coding: utf-8 -*-
import sys
from os.path import join, dirname
from setuptools import setup, find_packages

VERSION = (1, 0, 5)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = open(join(dirname(__file__), 'README.md'))
long_description = f.read().strip()
f.close()

install_requires = [
    "stream-connect==1.0.4"
]

setup(
    name = "publish-notifier",
    description = "Python library to notify a service of the published/consumed data",
    url = "https://github.com/anmolagarwal001/publish-notifier-py",
    long_description = long_description,
    version = __versionstr__,
    author = "Anmol Agarwal",
    author_email = "anmol.agarwal001@gmail.com",
    packages=['publish_notifier'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=install_requires,
    license='LICENSE',
    download_url='https://github.com/anmolagarwal001/publish-notifier-py/archive/v1.0.5.tar.gz'
)
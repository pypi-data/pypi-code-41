#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs

try:
    codecs.lookup("mbcs")
except LookupError:
    ascii = codecs.lookup("ascii")
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == "mbcs"))

VERSION = "0.2.4"
URL = "https://github.com/meta-source/meta1-python"

setup(
    name="meta1",
    version=VERSION,
    description="Python library for meta1",
    long_description=open("README.md").read(),
    download_url="{}/tarball/{}".format(URL, VERSION),
    author="Rostislav Gogolauri",
    author_email="invest@lampgram.com",
    maintainer="Rostislav Gogolauri",
    maintainer_email="invest@lampgram.com",
    url=URL,
    keywords=["meta1", "library", "api", "rpc"],
    packages=["meta1", "meta1api", "meta1base"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
    ],
    install_requires=open("requirements.txt").readlines(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
)

"""Setuptools entry point."""

import os
import codecs
from setuptools import setup, find_packages

from humilis_stream_gtw import __version__, __author__

dirname = os.path.dirname(__file__)
description = "Deploy an AWS API Gateway to Kinesis and/or Firehose"

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    if os.path.isfile("README.md"):
        long_description = codecs.open(os.path.join(dirname, "README.md"),
                                       encoding="utf-8").read()
    else:
        long_description = description

setup(
    name="humilis-stream-gtw",
    include_package_data=True,
    package_data={
        "": ["*.j2", "*.yaml"]},
    packages=find_packages(include=['humilis_stream_gtw',
                                    'humilis_stream_gtw.*']),
    version=__version__,
    author=__author__,
    author_email="german@findhotel.net",
    url="https://github.com/humilis/humilis-stream-gtw",
    license="MIT",
    description=description,
    long_description=long_description,
    install_requires=[
        "humilis>=1.5.5"],
    classifiers=[
        "Programming Language :: Python :: 3"],
    zip_safe=False,
    entry_points={
        "humilis.layers": [
            "stream-gtw=humilis_stream_gtw.plugin:get_layer_path"]}
)

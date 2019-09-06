#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().split()

setup(name='laiye-python-third-proto',
      version='0.1.1',
      description='Python laiye third proto',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Tang Ying',
      author_email='tangying@laiye.com',
      url="https://github.com/laiyethirdproto/laiye-python-third-proto.git",
      install_requires=requirements,
      license='MIT',
      packages=find_packages(exclude=["tests"]),
      )
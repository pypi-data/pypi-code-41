import setuptools
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cleverlab",
    version="0.0.3",
    author="Kai-Chun-Hsieh",
    author_email="cognitive@ars.de",
    description="A prototype SDK for using Cleverlab",
    packages=find_packages(),
    py_modules=['cleverlab', 'protocol', 'loader', 'common_pb2', 'login_pb2', 'devices'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
import setuptools
from distutils.core import setup, Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

rmsd_module = setuptools.Extension('naspy.rmsd', sources = ['naspy/rmsd.c'])

setuptools.setup(
    name="naspy",
    version="0.1.2",
    author="Jian Wang",
    author_email="jianopt@gmail.com",
    description="Nucleic Acids Structure Prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hust220/naspy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    ext_modules = [rmsd_module]
)

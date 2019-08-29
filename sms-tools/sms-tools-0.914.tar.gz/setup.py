from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

with open("README.md", "r") as fh:
    long_description = fh.read()

sourcefiles = ["smstools/utilFunctions.c", "smstools/cutilFunctions.pyx"]
extensions = Extension("cutilFunctions", sourcefiles, libraries=['m'], include_dirs=[numpy.get_include()])


setup(
    name="sms-tools",
    version="0.914",
    author="Music Technology Group",
    author_email="mtg-info@upf.edu",
    description="tools for sound analysis/synthesis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MTG/sms-tools",
    install_requires=['numpy'],
    package_data={"sms-tools":["smstools/*.so"]},
    packages=find_packages(),
    ext_modules = cythonize(extensions),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)

#!/usr/bin/env python
from setuptools import find_packages, setup, dist, Extension

dist.Distribution().fetch_build_eggs(['Cython>=0.29', 'numpy>=1.16'])

from Cython.Build import cythonize
import numpy

modules=[Extension('becke.becke', ["src/becke/becke.pyx"])]

setup(
    name="becke",
    version='0.0.14',
    description='Fast and memory efficient implementation of becke weights.',
    auther='Derrick Yang',
    author_email='yxt1991@gmail.com',
    url='https://github.com/tczorro/becke.git',
    package_dir={"": "src"},
    ext_modules=cythonize(modules),
    include_dirs=[numpy.get_include()],
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy>=1.16", "cython>=0.29"]
)

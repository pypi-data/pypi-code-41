#!/usr/bin/env python
""" tsplot is a Python package, built on matplotlib, for plotting time series data 
"""

from distutils.core import setup
from setuptools import find_packages

DOCLINES = (__doc__ or '').split("\n")
exec(open('tsplot/version.py').read())
setup(name='tsplot',
      version=__version__,
      description=DOCLINES[0],
      long_description="\n".join(DOCLINES[0:]),
      url='http://github.com/brett-hosking/tsplot',
      license='MIT',
      author='brett hosking',
      author_email='wilski@noc.ac.uk',
      install_requires=[
            "numpy>=1.16.4",
            "matplotlib>=2.2.3",
            "pandas>=0.23.4"
            # "requests>=2.22.0"
                ],
      packages=find_packages()
      )
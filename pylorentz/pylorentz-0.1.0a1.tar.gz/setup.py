"""
This script is used to install the package and all its dependencies. Run

    python setup.py install

to install the package.
"""

from setuptools import setup

def load_long_description(filename):
    """
    Loads the given file and returns its content.
    """
    with open(filename) as readme_file:
        content = readme_file.read()
        return content

setup(name='pylorentz',
      version='0.1.0-alpha.1',  # Also change in module
      packages=["pylorentz", "pylorentz.tests"],
      install_requires=["numpy"],
      test_suite='pylorentz.tests',
      description='Python project to work with 4-vectors and Lorentz boots in'
                  ' high energy physics.',
      long_description=load_long_description("README.rst"),
      url="https://gitlab.sauerburger.com/frank/pylorentz",
      author="Frank Sauerburger",
      author_email="frank@sauerburger.com",
      license="MIT",
      classifiers=["Intended Audience :: Science/Research",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
                   "Topic :: Scientific/Engineering :: Physics"])

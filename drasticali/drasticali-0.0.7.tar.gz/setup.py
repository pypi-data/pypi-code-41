import os
from setuptools import setup, find_packages

pkg = 'drasticali'
__version__ = '0.0.7'

build_root = os.path.dirname(__file__)
scripts = ["bin/" + j for j in os.listdir("bin") ]

def readme():
    """Get readme content for package long description"""
    with open(os.path.join(build_root, 'README.rst')) as f:
        return f.read()


def requirements():
    """Get package requirements"""
    with open(os.path.join(build_root, 'requirements.txt')) as f:
        return [pname.strip() for pname in f.readlines()]


setup(name=pkg,
      version=__version__,
      description="Diverse Radio Astronomy Software Tools for Imaging and Calibration",
      long_description=readme(),
      author="Athanaseus Ramaila",
      author_email="aramaila@ska.ac.za",
      packages=find_packages(),
      url="https://github.com/Athanaseus/Drastic",
      license="GNU GPL 3",
      classifiers=["Intended Audience :: Developers",
                   "Programming Language :: Python :: 3",
                   "Topic :: Scientific/Engineering :: Astronomy",
                   "Topic :: Software Development :: Libraries :: Python Modules"],
      platforms=["OS Independent"],
      scripts=scripts,
      include_package_data=True,
      install_requires=requirements())

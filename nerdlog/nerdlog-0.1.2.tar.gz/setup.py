import nerdlog
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nerdlog',
    version=nerdlog.__version__,
    copyright=nerdlog.__copyright__,
    author=nerdlog.__author__,
    author_email=nerdlog.__author_email__,
    description=nerdlog.__description__,
    long_description=long_description,
    license=nerdlog.__license__,
    packages=['nerdlog'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)

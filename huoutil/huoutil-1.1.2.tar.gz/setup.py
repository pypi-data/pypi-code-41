from distutils.core import Extension
from setuptools import setup
import huoutil
import os

setup(
    name='huoutil',
    version=huoutil.__version__,
    description=huoutil.__description__,
    author=huoutil.__author__,
    author_email=huoutil.__author_email__,
    packages=['huoutil'],
)

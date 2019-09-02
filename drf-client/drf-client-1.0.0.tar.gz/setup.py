import os
from codecs import open as codecs_open

from setuptools import find_packages
from setuptools import setup

base_dir = os.path.abspath(os.path.dirname(__file__))

with codecs_open(base_dir + '/README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drf-client',
    author='Deepak Sheoran',
    version='1.0.0',
    description='Dynamic rest client for DRF based django api servers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python", "Programming Language :: Python :: 3"
    ],
    url="https://github.com/sheoran/django-drf-client.git",
    packages=find_packages(exclude=['tests']),
    install_requires=['zope.cachedescriptors', 'coreapi', 'dotmap'],
    zip_safe=False,
)

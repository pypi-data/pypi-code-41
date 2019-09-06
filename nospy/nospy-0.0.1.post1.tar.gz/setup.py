"""
Setup script for NOSpy
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
version = "0.0.1-1" #NOTE: please blame pypy for the weird version numbers...

setup(
    name='nospy',
    version=version,
    description="Network Object Store",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dsikes/nospy',
    author='Dan Sikes',
    author_email='dsikes@atlantean.io',
    keywords='network object store binary data datastore fast',
    packages=find_packages(),
    install_requires=['requests'],

    project_urls={
        'Source': 'https://github.com/dsikes/nospy',
    },
)
from setuptools import setup
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(file_name):
    """Read a text file and return the content as a string."""
    with open(os.path.join(os.path.dirname(__file__), file_name),
              encoding='utf-8') as f:
        return f.read()


def get_version(txt):
    return re.search(r'\d{1,3}\.\d{1,3}(?:.\d{1,3})?', txt).group(0)


setup(
    name='epflldap',
    version=get_version(read('epflldap/_version.py')),
    author='Raphaël Rey',
    author_email='raphael.rey@epfl.ch',
    packages=['epflldap', 'epflldap.db', 'epflldap.users'],
    license='MIT',
    description="Ce module permet de d'analyser les données d'LDAP à l'EPFL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
       "pandas",
       "ldap3"
    ],
)

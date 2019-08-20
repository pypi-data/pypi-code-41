# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------
# coding: utf-8

from setuptools import setup, find_packages

NAME = "EnergyCapSdk"
VERSION = "7.5.2251"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["msrest>=0.2.0"]

setup(
    name=NAME,
    version=VERSION,
    description="EnergyCapApi",
    author_email="",
    url="",
    keywords=["Swagger", "EnergyCapApi"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    EnergyCAP API
    """
)

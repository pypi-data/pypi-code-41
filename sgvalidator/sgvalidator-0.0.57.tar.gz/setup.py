import pkg_resources
from setuptools import setup, find_packages

VERSION_FILEPATH = pkg_resources.resource_filename("sgvalidator", "VERSION")
with open(VERSION_FILEPATH, "r") as f:
    VERSION = f.read()

setup(
    name='sgvalidator',
    version=VERSION,
    author="noah",
    author_email="info@safegraph.com",
    packages=find_packages(),
    test_suite='nose.collector',
    include_package_data=True,
    tests_require=['nose'],
    install_requires=[
        "termcolor==1.1.0",
        "phonenumbers==8.10.13",
        "zipcodes==1.0.5",
        "us==1.0.0",
        "usaddress",
        "uszipcode",
        "pandas"  # no need to pin this to a specific version
    ],
    zip_safe=False
)

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

from setuptools import find_packages, setup

with open("README.rst", "rb") as fp:
    LONG_DESCRIPTION = fp.read().decode("utf-8").strip()


setup(
    name="cfme_testcases",
    use_scm_version=True,
    url="https://gitlab.com/mkourim/cfme-testcases",
    description="Create new testrun and upload missing testcases using Polarion Importers",
    long_description=LONG_DESCRIPTION,
    author="Martin Kourim",
    author_email="mkourim@redhat.com",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    entry_points={"console_scripts": ["cfme_testcases_upload.py = cfme_testcases.cli:main"]},
    setup_requires=["setuptools_scm"],
    install_requires=["dump2polarion>=0.40.0", "six", "python-box"],
    keywords=["polarion", "testing"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
)

# -*- coding: utf-8 -*-

import os
from codecs import open

from setuptools import find_packages, setup


NAME = "aws-key-formatter"
DESCRIPTION = ""
AUTHOR = "Kelton Karboviak"
EMAIL = "kelton.karboviak@gmail.com"
URL = "https://github.com/KeltonKarboviak/aws-key-formatter"

REQUIRED = ["boto3>=1.9,<2.0", "click>=7.0,<8.0"]

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(here, "src")


def read(filename):
    with open(os.path.join(here, filename), "r", encoding="utf-8") as fp:
        return fp.read()


long_description = read("README.md")
changelog = read("CHANGELOG.md")
license_terms = read("LICENSE.md")


about = {}
project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
exec(read(os.path.join(src_dir, project_slug, "__version__.py")), about)


setup(
    name=NAME,
    version=about["__version__"],
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=long_description + "\n\n" + changelog + "\n\n" + license_terms,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["aws-key-formatter=aws_key_formatter.cli:main"]},
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        # 'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent",
    ],
)

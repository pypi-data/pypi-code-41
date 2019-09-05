from sys import exit, version_info
from setuptools import setup, find_packages
from os import environ
import logging
import emmtyper

logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))

if version_info <= (3, 0):
    logging.fatal("Sorry, requires Python 3.x, not Python 2.x\n")
    exit(1)


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=emmtyper.__name__,
    version=emmtyper.__version__,
    description=emmtyper.__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=emmtyper.__url__,
    author=emmtyper.__author__,
    author_email=emmtyper.__email__,
    maintainer=emmtyper.__maintainer__,
    maintainer_email=emmtyper.__maintainer_email__,
    license=emmtyper.__license__,
    python_requires=">=3.6, <4",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    zip_safe=False,
    install_requires=["scipy>=1.1.0", "numpy>=1.15.0", "python-dateutil", "click"],
    test_suite="nose.collector",
    tests_require=["nose"],
    entry_points={
        "console_scripts": [
            "emmtyper=emmtyper.bin.run_emmtyper:main",
            "emmtyper-db=emmtyper.utilities.make_db:emmtyper_db",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: Implementation :: CPython",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    package_data={"emmtyper": ["data/*", "db/*"]},
)

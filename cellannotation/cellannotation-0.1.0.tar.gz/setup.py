#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

NAME = 'cellannotation'
VERSION = "0.1.0"

AUTHOR = 'Bioinformatics Laboratory, FRI UL'
AUTHOR_EMAIL = 'contact@orange.biolab.si'

URL = 'http://biolab.si/'
DESCRIPTION = 'Package for annotating the data (e.g. cell data).'
with open('README.md') as f:
    README = f.read()

KEYWORDS = [
    'cells',
    'annotation'
]
PACKAGES = find_packages()

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))
) - {''})


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=README,
        packages=PACKAGES,
        keywords=KEYWORDS,
        install_requires=INSTALL_REQUIRES,
        test_suite='cell_annotation.tests.suite',
        classifiers=[
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 4 - Beta"
        ]
    )

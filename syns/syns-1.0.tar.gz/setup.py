#!/usr/bin/env python3
import syns.syns as syns
from setuptools import setup , find_packages

def main():
    setup(
            name = "syns",
            version = syns.VERSION,
            author = "Jan Fecht",
            description = "Query German synonyms from openthesaurus.de",
            url = "https://github.com/boi4/syns/",
            packages = find_packages(),
            install_requires = ["requests"],
            entry_points = {
                    'console_scripts': [ 'syns = syns.syns:main' ]
                }
        )

if __name__ == '__main__':
    main()

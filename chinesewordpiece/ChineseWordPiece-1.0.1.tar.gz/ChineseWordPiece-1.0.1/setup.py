#!/usr/bin/env python
#-*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "ChineseWordPiece",
    version = "1.0.1",
    keywords = ("pip", "ChineseWordPiece", "WordPiece"),
    description = "WordPiece for Chinese Words",
    long_description = "WordPiece for Chinese Words",
    license = "MIT Licence",

    url = "https://github.com/soap117/ChineseWordPiece",
    author = "Junyu Luo",
    author_email = "asbljy@outlook.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
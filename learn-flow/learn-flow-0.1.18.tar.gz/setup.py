# -*- coding: utf-8 -*-
"""
setup.py
------------
learn-flow setup script.
TODO: change the framework name to Flow/Soul
"""
from setuptools import setup, find_packages
# builds the project dependency list
install_requires = None
with open('requirements.txt', 'r') as f:
    install_requires = f.readlines()

# setup function call
setup(
    name="learn-flow",
    version="0.1.18",
    author="Luis Felipe Muller",
    author_email="luisfmuller@gmail.com",
    description=("An Structural framework to create machine learning models using tensorflow."),
    keywords="",
    # Install project dependencies
    install_requires=install_requires,

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md', "*.json", "*.zip"],
    },
    include_package_data=True,
    packages=find_packages(exclude=["*tests"]),
)

from setuptools import setup, find_packages
from pathlib import Path
import os

with open("README.md") as f:
    readme = f.read()

setup(
    name="alacritty-color-switcher",
    version="0.1.2",
    description="Apply color schemes to your alacritty config.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Timm Behner",
    author_email="behner@cs.uni-bonn.de",
    url="https://github.com/tbehner/alacritty-color-switcher",
    install_requires=["click", "ruamel.yaml"],
    packages=find_packages(exclude=("tests", "docs")),
    package_data = {'': ['*.yaml']},
    entry_points={"console_scripts": ["acs=alacritty_color_switcher.cli:main"]},
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7"
        ]
)

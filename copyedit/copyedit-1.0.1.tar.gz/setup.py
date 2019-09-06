#!/usr/bin/env python3
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="copyedit",
      version="1.0.1",
      description="An easy way to edit your clipboard contents!",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/Rayquaza01/copyedit",
      author="Rayquaza01",
      author_email="rayquaza01@outlook.com",
      license="MIT",
      scripts=["bin/copyedit.py"],
      install_requires=["pyperclip"],
      include_package_data=True,
      package_data={"": ["README.md"]},
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"
      ])

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name="fx2obp",
  version='0.2',
  description="Convert exchange rates to OBP format, and optionally post to an OBP instance",
  url="https://github.com/chrisjsimpson/fx2obp",
  author="Chris Simpson",
  author_email="chris15leicester@gmail.com",
  long_description=long_description,
  long_description_content_type="text/markdown",
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
  ),
  packages=['fx2obp'],
  install_requires=[
    'bs4',
    'requests'
  ]
)

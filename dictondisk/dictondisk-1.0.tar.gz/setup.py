import dictondisk
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
  name = "dictondisk",
  py_modules = ["dictondisk"],
  license = dictondisk.__license__,
  version = dictondisk.__version__,
  description = dictondisk.__description__,
  long_description = readme,
  long_description_content_type = "text/markdown",
  author = dictondisk.__author__,
  author_email = dictondisk.__email__,
  url = dictondisk.__url__,
  keywords = "dictionary dict disk pickle",
  classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3 :: Only",
  ],
)

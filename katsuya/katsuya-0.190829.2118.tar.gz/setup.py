import setuptools

def create_version():
  """Returns e.g. "0.991231.2359"."""
  import datetime
  now = datetime.datetime.now()
  s = now.strftime("0.%y%m%d.%H%M")
  return s

with open("README.md") as f:
  long_description = f.read()

setuptools.setup(
  # The distribution name. It also must not already taken on pypi.org.
  name="katsuya",
  # PEP 440 -- Version Identification and Dependency Specification
  version=create_version(),
  author="yoichikatsuya",
  author_email="yoichi.katsuya@gmail.com",
  # A one-sentence summary.
  description="A small example package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  # The URL for the homepage of the project. It's necessary.
  url="https://example.com/",
  packages=setuptools.find_packages(),
  classifiers=[
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
  ]
)

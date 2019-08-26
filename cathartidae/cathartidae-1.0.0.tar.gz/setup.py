from os import path
from setuptools import setup, find_packages

with open(path.join("requirements.txt")) as req:
    # handles custom package repos
    requirements = [requirement for requirement in req.read().splitlines() if not requirement.startswith("-")]

setup(name="cathartidae",
      version="1.0.0",
      install_requires=requirements,
      description="decorators for reducing nesting",
      keywords="code reuse nesting reduction",
      url="https://github.com/MATTHEWFRAZER/cathartidae",
      author="Matthew Frazer",
      author_email="mfrazeriguess@gmail.com",
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False,
      )
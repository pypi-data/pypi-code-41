from qai.version import __version__

import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


requirementPath = os.path.abspath("./requirements.txt")
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(
    name="qai",
    packages=find_packages(),
    author="Qordoba",
    author_email="sam.havens@qordoba.com",
    url="https://github.com/Qordobacode/library.qai.utilities",
    version=__version__,
    license="unlicensed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
)

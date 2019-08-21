import pathlib
from setuptools import setup, find_packages
from distutils.util import convert_path

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

#Load the meta data from the module to have one source for the version and other data
meta = {}
aboutPath = convert_path('styletransfer/__about__.py')
with open(aboutPath) as aboutFile:
    exec(aboutFile.read(), meta)

#Load the requirements form the file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name=meta['__title__'],
    version=meta['__version__'],
    description=meta['__summary__'],
    author=meta['__author__'],
    author_email=meta['__email__'],
    license=meta['__license__'],
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False
)

from setuptools import setup, find_packages
import re

VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
VERSIONFILE = "pinda/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'pinda',
    version = verstr,
    author = 'Charlie Laughton',
    author_email = 'charles.laughton@nottingham.ac.uk',
    description = 'Pip-INstallable Dockerized Applications',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://bitbucket.org/claughton/pinda',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
    ],
    packages = find_packages(),
    scripts = [
        'scripts/pinda',
    ],
    install_requires = [
        'requests',
        'pyyaml',
    ],
)

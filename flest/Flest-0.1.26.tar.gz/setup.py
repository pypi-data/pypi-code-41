import re
import pathlib
from setuptools import setup
from setuptools import find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION = (HERE / "src" / "flest" / "__init__.py")


def read(filename):
    with open(filename, 'r') as fp:
        return fp.read()


def find_version():
    version_file = read(VERSION)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="Flest",
    version=find_version(),
    description="Flest - small contribution to Flask world.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://tbd",
    author="Jihwan Song",
    author_email="jihwan2@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=["Flask", "decorator"],
    test_requires=[
        "pytest",
        "pytest-cov",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "flest=flest.cli:main",
        ]
    },
)

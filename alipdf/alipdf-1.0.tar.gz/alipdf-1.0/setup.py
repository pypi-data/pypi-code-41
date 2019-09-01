import setuptools
from pathlib import Path

setuptools.setup(
    name="alipdf",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packaages=setuptools.find_packages(exclude=["tests", "data"])
)
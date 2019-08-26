import subprocess
import sys

from setuptools import find_packages, setup

__version__ = "1.1.2"


setup(
    name="maetema",
    version=__version__,
    description="Tema de MaeDocs",
    url="https://docs.maeorg.site",
    author="Ham Won Trikru",
    author_email="lwonderlich@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"maeguias.themes": ["mae = maetema"]},
)

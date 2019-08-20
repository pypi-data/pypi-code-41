import setuptools
from parpar import __version__, __name__
with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
    name=__name__,
    version=__version__,
    author="Sumner Magruder",
    author_email="sumner.magruder@zmnh.uni-hamburg.de",
    description="Parallel parser for large files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/parpar/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

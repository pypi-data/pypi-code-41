import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
README += (HERE / "CHANGELOG.md").read_text()

# This call to setup() does all the work
setup(
    name="savior",
    version="0.2.3",
    description="Flexible immutable entity database",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/elibdev/savior",
    author="Eli B",
    author_email="eli@formal.studio",
    license="ISC",
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["savior"],
    include_package_data=True,
    install_requires=["lmdb", 'msgpack'],
)


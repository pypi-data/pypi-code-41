import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = "stub" # (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="deno",
    version="0.0.0",
    description="python ffi for deno ops",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hayd/deno-py",
    author="Andy Hayden",
    author_email="andyhayden1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["deno"],
    include_package_data=True,
)

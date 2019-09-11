
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="check-vat",
    version="0.1.0",
    author="Christoph Becker",
    author_email="tuergeist@gmail.com",
    description="Checks if a given string is a valid (real, registered) European VAT ID",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuergeist/check-vat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # test_suite="tests",
)

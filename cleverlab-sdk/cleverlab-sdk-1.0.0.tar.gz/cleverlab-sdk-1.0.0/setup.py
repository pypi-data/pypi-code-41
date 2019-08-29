import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cleverlab-sdk",
    version="1.0.0",
    author="Kai-Chun-Hsieh",
    author_email="cognitive@ars.de",
    description="A prototype SDK for using Cleverlab",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
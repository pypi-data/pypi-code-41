import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fetchDBconn",
    version="0.0.9",
    author="Krishna Sailesh Pydimarri",
    author_email="krishnasailesh93@gmail.com",
    description="Fetch db conn details from AWS secret manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krishna-pydimarri/dbconn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 


from setuptools import setup, find_packages

def long_description():
    with open("README.md") as infile:
        return infile.read()

def license():
    return "MIT License"

long_description_content_type="text/markdown"

setup(
    name="AzurePyProxy",
    version="1.0b",
    packages=find_packages(),
    author="Tomas Votava",
    author_email="info@tomasvotava.eu",
    description="This package provides proxy class for calling azure commands directly from Python.",
    keywords="azure platform azure python proxy",
    url="https://github.com/tomasvotava/azure-pyproxy",
    project_urls={
        "Bug Tracker": "https://github.com/tomasvotava/azure-pyproxy/issues",
        "Documentation": "https://github.com/tomasvotava/azure-pyproxy/blob/master/README.md",
        "Source Code": "https://github.com/tomasvotava/azure-pyproxy"
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "Development Status :: 4 - Beta"
    ],
    long_description=long_description(),
    download_url="https://github.com/tomasvotava/azure-pyproxy/archive/master.zip",
    license=license(),
    long_description_content_type="text/markdown"
)


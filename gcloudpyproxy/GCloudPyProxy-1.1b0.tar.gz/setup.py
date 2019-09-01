from setuptools import setup, find_packages

def long_description():
    with open("README.md") as infile:
        return infile.read()

def license():
    return "MIT License"

long_description_content_type="text/markdown"

setup(
    name="GCloudPyProxy",
    version="1.1b",
    packages=find_packages(),
    author="Tomas Votava",
    author_email="info@tomasvotava.eu",
    description="This package provides proxy class for calling gcloud commands directly from Python.",
    keywords="gcp google cloud platform gcloud python proxy",
    url="https://github.com/tomasvotava/gcloud-pyproxy",
    project_urls={
        "Bug Tracker": "https://github.com/tomasvotava/gcloud-pyproxy/issues",
        "Documentation": "https://github.com/tomasvotava/gcloud-pyproxy/blob/master/README.md",
        "Source Code": "https://github.com/tomasvotava/gcloud-pyproxy"
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "Development Status :: 4 - Beta"
    ],
    long_description=long_description(),
    download_url="https://github.com/tomasvotava/gcloud-pyproxy/archive/master.zip",
    license=license(),
    long_description_content_type="text/markdown"
)


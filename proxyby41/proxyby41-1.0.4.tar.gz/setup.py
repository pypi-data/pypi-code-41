import pathlib
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()
setup(
    name="proxyby41",
    version="1.0.4",
    description="Scrape All Types Of Proxies In A Click",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/41_alderson/proxyby41",
    author="Anirudh Alderson",
    author_email="ano1425mous@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        ],
    )

import pathlib
from setuptools import setup, setuptools

with open('README.md', 'r') as f:
    long_description = f.read()
setup(
    name="proxyby41",
    version="0.1",
    description="Scrape All Types Of Proxies In A Click",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/41_alderson/proxyby41",
    author="Anirudh Alderson",
    author_email="ano1425mous@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests', 'bs4'
    ],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        ],
    )

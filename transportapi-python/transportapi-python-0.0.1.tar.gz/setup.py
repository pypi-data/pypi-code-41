from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="transportapi-python",
    version="0.0.1",
    author="Dextroz",
    description="Unofficial Python 3.7 API wrapper for the TransportAPI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dextroz/transportapi-python",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="Wrapper API Transport TransportAPI Library Car Bus Bike Public Bicycle Train",
)
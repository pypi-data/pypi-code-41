import pathlib
# import os
import setuptools

with open("README.txt", "r") as fh:
    README = fh.read()


# This call to setup() does all the work

setuptools.setup(
    name="otlpytools",
    version="1.0.6",
    description="Log all python files, and push to Splunk",
    long_description=README,
    long_description_content_type="text/plain",
    author="Stefan McShane",
    author_email="stefan.mcshane@options-it.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["pyyaml", "requests"],
    entry_points={
        "console_scripts": [
            "otlpylogga=otlpylogga.__main__:main",
        ]
    },
)

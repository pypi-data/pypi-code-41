"""
NeurodataLab LLC 19.07.2019
Created by Andrey Belyaev
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ndl-api",
    version="0.3.2",
    author="Neurodata Lab",
    author_email="admin@neurodatalab.dev",
    description="Neurodata Lab API tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'Pillow>=6.1',
        'grpcio>=1.22',
        'grpcio-tools>=1.22'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
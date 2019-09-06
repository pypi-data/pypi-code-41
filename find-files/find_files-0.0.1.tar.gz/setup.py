'''
Created on 03-Sep-2019

@author: elango
'''
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="find_files",
    version="0.0.1",
    author="Elango SK",
    author_email="elango111000@gmail.com",
    description="To find the file by using name and extension for your given directory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elaa0505/find_files",
    packages=setuptools.find_packages(),
    keywords = "Find files, find files using pattern",
    
)

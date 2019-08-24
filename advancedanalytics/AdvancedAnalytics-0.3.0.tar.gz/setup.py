#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:44:15 2019

@author: EJones
"""
import setuptools

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="AdvancedAnalytics", 
    version="0.3.0", 
    author="Edward R Jones", 
    author_email="ejones@tamu.edu", 
    url="https://github.com/tandonneur/AdvancedAnalytics", 
    description="Python support for 'The Art and Science of Data Analytics'",
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
)

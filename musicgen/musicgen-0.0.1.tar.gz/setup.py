#!/usr/bin/env python
# coding: utf-8

# In[11]:


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="musicgen",
    version="0.0.1",
    license='MIT',
    keywords = ['LSTM', 'Sequence models', 'RNN','Neural network','Music generation'],
    author="Ranjith M S",
    author_email="ranjithms523@gmail.com",
    description="A module for pre-processing steps in music generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ranjith-ms",
    download_url ="https://github.com/ranjith-ms/musicgen/archive/v0.1.tar.gz",
    packages=setuptools.find_packages(),
    install_requires=["youtube_dl", "music21","numpy",],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
)


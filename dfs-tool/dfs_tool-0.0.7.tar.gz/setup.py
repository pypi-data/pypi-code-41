import os
from setuptools import setup

# The directory containing this file
HERE = os.path.dirname(os.path.abspath(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md"), "r") as f:
    README = f.read()

# This call to setup() does all the work
setup(
    name="dfs_tool",
    version="0.0.7",
    description="Hadoop HDFS cli",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/stonezhong/dfs_tool",
    author="Stone Zhong",
    author_email="stonezhong@hotmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["dfs_tool"],
    install_requires=["pywebhdfs"],
    entry_points={
        "console_scripts": [
            "dfs_tool=dfs_tool:main",
        ]
    },
)

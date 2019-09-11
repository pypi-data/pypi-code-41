#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import setuptools

version = ""
with open('ariestools/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ariestools",
    version=version,
    author="jasonzhang",
    author_email="864040015@qq.com",
    description="Common Tools for python lib",
    url="",
    install_requires=[
        'requests>=2.22.0',
        'urllib3>=1.25.3',
        'PyYAML>=5.1'
    ],
    packages=setuptools.find_packages(exclude=("test")),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
    exclude_package_data=
    {'':
        [
            "ariestools/graphql_query_util.py",
            "ariestools/json_path_util.py",
            "ariestools/json_util.py",
            "ariestools/path_util.py",
            "ariestools/yaml_util.py"
        ]
    },
)

"""Python Package Definition."""

import os
from setuptools import find_packages, setup


root = os.path.dirname(__file__)
src = os.path.relpath(os.path.join(root, "python"))
readme = open(os.path.join(root, "README.md")).read()

setup(
    name="glossy",
    version="0.0.3",
    description="Make your decorators glossy!",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ylathouris/glossy",
    author="Yani Lathouris",
    author_email="ylathouris@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7, <4",
    keywords=(
        "decorator, decorators, "
        "test, testing, mock, mocks, stub, stubs, stubbing, "
        "util, utils, utility, utilities, helpers, tools, "
        "wrappers"
    ),
    project_urls={
        "Say Thanks!": "http://saythanks.io/to/ylathouris",
        "Source": "https://github.com/ylathouris/glossy",
        "Tracker": "https://github.com/ylathouris/glossy/issues",
    },
    package_dir={"": src},
    packages=find_packages(src),
    install_requires=[],
)

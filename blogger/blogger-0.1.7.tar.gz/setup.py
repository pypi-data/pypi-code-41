# !/usr/bin/env python3

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="blogger",
    version="0.1.7",
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    setup_requires=["wheel"],
    description="Command line utility for converting text to speech.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Buster Technologies",
    license="MIT",
    author_email="holden@bustererp.com",
    url="https://github.com/bustertechnologies/blogger",
    keywords=[],
    python_requires=">=3.4",
    install_requires=["click==7.*", "colorama==0.*", "gTTS==2.0.*", "beautifulsoup4==4.*", "html2text", "lxml"],
    entry_points={"console_scripts": ["blogger=blogger.cli:main"]},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
    ],
)

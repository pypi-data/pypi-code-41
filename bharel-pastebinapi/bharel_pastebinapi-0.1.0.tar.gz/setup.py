import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bharel_pastebinapi",
    version="0.1.0",
    description="An API for pastebin",
    long_description=long_description,
    long_description_content_type='text/markdown',
    download_url="https://github.com/bharel/pastebinapi/archive/0.1.0.tar.gz",
    author="Bar Harel",
    author_email="bzvi7919+pastebinapi@gmail.com",
    url="https://github.com/bharel/pastebinapi",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "lxml",
        "python-dateutil"
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="brownieSort",
    version="0.0.4",
    author="Alex Peden",
    author_email="apeden23@gmail.com",
    description="For sorting brownies into tent groups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    ##url="https://github.com/apeden/brownieSorter",
    download_url="https://github.com/apeden/brownieSorter/archive/0.0.4.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


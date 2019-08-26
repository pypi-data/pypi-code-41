import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shrek",
    version="0.0.2",
    author="Michael E. Vinyard",
    author_email="mvinyard@mgh.harvard.com",
    description="A package for scATAC-seq pre-processing",
    long_description="Stringing togeter several common and currently used tools for scATAC-seq preprocessing. From this simple command line interface, one can quicky and easily initiate commands to create all tht is needed to perform downstream analysis such as clustering, trajectory inference, etc.)",
    long_description_content_type="text/markdown",
    url="https://github.com/mvinyard/shrek",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

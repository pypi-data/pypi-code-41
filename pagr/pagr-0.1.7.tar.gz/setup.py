import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pagr",
    version="0.1.7",
    author="Alexander Hungenberg",
    author_email="alexander.hungenberg@gmail.com",
    description="A Python Aggregator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/defreng/python-pagr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

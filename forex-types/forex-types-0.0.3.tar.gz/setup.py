import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="forex-types",
    version="0.0.3",
    author="Andrew Allaire",
    author_email="andrew.allaire@gmail.com",
    description="Basic Forex classes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aallaire/python_forex_types",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

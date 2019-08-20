import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dictol",
    version="0.1.0",
    author="Tiep Vu",
    author_email="vuhuutiep@gmail.com",
    description="A Toolbox for Discriminative Dictionary Learing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiepvupsu/dictol_python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


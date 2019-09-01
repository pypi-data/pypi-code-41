import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="decompress",
    version="0.0.4",
    author="Kevin Bird",
    author_email="kevinbird15@gmail.com",
    description="A library to help decompress multiple compression types",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/limeai/decompress",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
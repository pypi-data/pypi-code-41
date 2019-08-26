import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pythonhelpers",
    version="0.0.1pre",
    author="Thomas Kastl",
    author_email="thomas.kastl@daimler.com",
    description="A collection of Python tools. So far, just a test.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=["pythonhelpers"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
   'pandas',
   'pyspark']
)
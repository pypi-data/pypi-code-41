import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="batchflows",
    version="1.0.1b0",
    author="Paulo Porto",
    author_email="cesarpaulomp@gmail.com",
    description="library for executing batches of data processing sequentially or asynchronously to python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/pcmporto/batchflows/src/master",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

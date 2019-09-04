import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sliceup",
    version="0.0.4",
    author="SliceUp, Inc",
    author_email="info@sliceup.com",
    description="Python client for SliceUp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sliceup/sliceup-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

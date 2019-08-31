import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SQLAPI-Timaos",
    version="0.0.1",
    author="Timaos",
    author_email="201436009@uibe.edu.cn",
    description="used to run certain kinds of sql in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Timaos123/SQLAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
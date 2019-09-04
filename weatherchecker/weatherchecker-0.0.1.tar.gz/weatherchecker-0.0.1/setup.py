import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="weatherchecker",
    version="0.0.1",
    author="Roney Mathew",
    author_email="roneyelirickal@gmail.com",
    description="A small weather crawling package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/weatherchecker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
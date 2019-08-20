import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gtfinder",
    version="1.1",
    author="Ettore d'Angelo",
    author_email="ettoredangelo97@gmail.com",
    description="A package to create and analyze dynamic games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ettoredangelo/gtfinder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


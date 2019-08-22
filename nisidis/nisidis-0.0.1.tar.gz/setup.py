import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nisidis",
    version="0.0.1",
    author="Christos Palyvos",
    author_email="chpalyvos@gmail.com",
    description="A small nisidis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chpalyvos/ap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

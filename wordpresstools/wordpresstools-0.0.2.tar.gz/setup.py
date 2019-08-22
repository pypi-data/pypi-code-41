import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wordpresstools",
    version="0.0.2",
    author="Matthew Larsen",
    author_email="matt.larsen@connorgp.com",
    description="A small set of tools for administration of WordPress installations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matt-larsen-sld/wptools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
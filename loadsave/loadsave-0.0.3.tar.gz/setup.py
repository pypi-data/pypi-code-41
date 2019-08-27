import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loadsave",
    version="0.0.3",
    author="Joel Stansbury",
    author_email="stansbury.joel@gmail.com",
    description="One-line loading and saving to/from various file formats (csv, wav, pkl, json)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoelStansbury/Datastore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vmtlib",
    version="0.0.1",
    author="Philip Meier",
    description="A simple parser for Valve Material Type (.vmt) files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/megaprokoli/vmtlib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
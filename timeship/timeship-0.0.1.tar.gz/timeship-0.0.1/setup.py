import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeship",
    version="0.0.1",
    author="Nollde",
    description="Easy timing of all kinds of python code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.rwth-aachen.de/dennis.noll/timeship.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twissreader",
    version="0.0.5",
    author="Christian Staufenbiel",
    author_email="christian.staufenbiel@cern.ch",
    description="Reading Twiss-files created by MAD-X",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/cstaufen/twissreader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arglabels",
    version="0.0.2",
    author="Michael Harms",
    author_email="michaelharms95@icloud.com",
    description="A simple decorator to enable Swift-like argument labels for functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michael-harms/arglabels",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

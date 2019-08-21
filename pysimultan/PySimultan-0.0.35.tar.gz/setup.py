import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PySimultan",
    version="0.0.35",
    author="Maximilian Buehler",
    author_email="maximilian.buehler@tuwien.ac.at",
    description="SIMULTAN API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bph-tuwien/PySimultan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

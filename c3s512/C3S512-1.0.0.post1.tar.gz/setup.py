import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="C3S512",
    version="1.0.0post1",
    author="Jesús Peña-Izquierdo & Iván Cernicharo",
    author_email="jesus.pena@bsc.es",
    description="Monitor of download activity from the Climate Data Store for quality control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

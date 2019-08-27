import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aios-lib",
    version="0.0.1",
    author="Mandy",
    author_email="mandy.zhang@clustar.ai",
    description="aios lib package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.clustarai.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python ",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


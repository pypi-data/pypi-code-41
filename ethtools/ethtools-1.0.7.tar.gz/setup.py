import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ethtools",
    version="1.0.7",
    author="TakeWing",
    author_email="n.ostroukhov@takewing.ru",
    description="EthTools framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TakeWingCo/eth-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

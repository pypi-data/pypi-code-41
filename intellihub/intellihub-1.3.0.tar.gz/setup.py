import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intellihub",
    version="1.3.0",
    author="Spotflock LLC",
    author_email="connect@spotflock.com",
    description="Python Client for Intellihub.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Spotflock/intellihub-sdk-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


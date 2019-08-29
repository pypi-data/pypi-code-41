import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seedling",
    version="0.0.1",
    author="Andre Fu",
    author_email="andrefu.af@hotmail.com",
    description="A Synthetic Biology Machine Learning package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andre-fu/seedling",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
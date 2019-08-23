import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="actionfreeze",
    version="0.0.1",
    author="Alan Rios",
    author_email="alanrioscosta@yahoo.com",
    description="Schedule a function to run repeatedly for a while.",
    long_description="Schedule a function to run repeatedly for a while. As long as it does not exceed 1 minute",
    long_description_content_type="text/markdown",
    url="https://github.com/hirios/actionfreeze",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

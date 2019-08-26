import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cache-function-deepakmishra",
    version="0.0.2",
    author="Deepak Mishra",
    author_email="deepakmishra117@gmail.com",
    description="A small decorator which helps cache a result of a function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deepakmishra/cache_function",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: Freeware",
        "Operating System :: OS Independent",
    ],
)

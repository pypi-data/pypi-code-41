import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mython3",
    version="0.0.1.6",
    author="Will F",
    author_email="forsbergw82@gmail.com",
    description="LOTS OF NEW METHODS!!!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['mython3'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)

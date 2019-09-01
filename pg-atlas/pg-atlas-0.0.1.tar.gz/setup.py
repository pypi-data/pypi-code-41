import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pg-atlas",
    version="0.0.1",
    author="Ishkhan Verdyan",
    author_email="vermasstud@gmail.com",
    description="Simple Image Atlas creator for Pygame framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damaskes/pg-atlas",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
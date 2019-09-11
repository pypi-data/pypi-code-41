import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="digit-index",
    version="1.0",
    author="Artem Konyshev",
    author_email="konyshev.ar@gmail.com",
    description="Package for effectively finding digit on certain index in infinite number string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KonyshevArtem/digit-index",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)

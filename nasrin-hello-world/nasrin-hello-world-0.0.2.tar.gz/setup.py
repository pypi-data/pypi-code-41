import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nasrin-hello-world",
    version="0.0.1",
    author="Nasrin",
    author_email="nasrin@kidocode.com",
    description="A sample hello world package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ntohidi/helloworld.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
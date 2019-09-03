import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-diff",
    version="0.1.0",
    author="Alvin Chen",
    author_email="alvinch.chen@moxa.com",
    description="A simple diff tool for dictionary and list",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alvinchchen/simple_diff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

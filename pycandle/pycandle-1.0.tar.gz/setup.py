from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

required = []
with open("requirements.txt", "r") as freq:
    for line in freq.read().split():
        required.append(line)

setup(
    name="pycandle",
    version="1.0",
    author="Christoph Schöller",
    description="PyCandle is a lightweight library for pytorch that makes running experiments easy, structured, repeatable and avoids boilerplate code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cschoeller/pycandle",
    packages=find_packages(),
    include_package_data=True,
    dependency_links=[],
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.5',
    install_requires = required
)
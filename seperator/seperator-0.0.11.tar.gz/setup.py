import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seperator",
    version="0.0.11",
    author="Erdem Aybek",
    author_email="eaybek@gmail.com",
    description=" ".join(
        [
            "eye catching and informative",
            "seperator utilities for long",
            "shell client outputs",
        ]
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaybek/seperator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

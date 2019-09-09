import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeself",
    version="0.0.1",
    author="Dagito",
    author_email="jodagito@gmail.com",
    description="""A library which allows to
    measure the execution time of an entire file.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jodagito/Timeself",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)

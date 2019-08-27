import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple_sql_abstraction",
    version="1.0.0",
    author="Pedro Ribeiro Baptista",
    author_email="prbpedro@gmail.com",
    description="Simple SQL abstraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prbpedro/simple_sql_abstraction",
    install_requires=[],
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

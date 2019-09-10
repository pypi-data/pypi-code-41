import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dataframe-column-identifier",
    version="0.0.4",
    author="Danilo Silva de Oliveira",
    author_email="danilooliveira28@hotmail.com",
    description="A light and useful package to find columns in a Dataframe by its values.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ds-oliveira/dataframe_column_identifier",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires='>=3.6',
)

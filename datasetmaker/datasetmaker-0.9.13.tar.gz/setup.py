import setuptools

requires = [
    "ddf_utils",
    "pandas",
    "lxml",
    "requests",
    "frame2package",
    "html5lib",
    "bs4",
    "xlrd",
    "scikit-learn",
    "spacy==2.0.12",
    "pyarrow",
]

setuptools.setup(
    name="datasetmaker",
    version="0.9.13",
    description="Fetch, transform, and package data.",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    install_requires=requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
)

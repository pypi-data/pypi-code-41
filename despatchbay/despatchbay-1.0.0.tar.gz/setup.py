import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="despatchbay",
    version="1.0.0",
    author="Scott Keenan",
    author_email="scott.keenan@thesalegroup.co.uk",
    description="Python SDK for the Despatch Bay API v15",
    install_requires=['suds-py3', 'requests'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/despatchbay/despatchbay-python-sdk",
    download_url="https://github.com/despatchbay/despatchbay-python-sdk/archive/v1.0.0.tar.gz",
    packages=setuptools.find_namespace_packages(include=['despatchbay']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

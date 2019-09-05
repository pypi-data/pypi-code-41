import setuptools

with open("containerregistry/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="containerregistry-ccwienk",
    version="0.2.5",
    author="Christian Cwienk",
    author_email="Christian.Cwienk@sap.com",
    description="a library and tools for interacting with container registries",
    long_description=long_description,
    # Make sure to have up-to-date setuptools, twine and wheel
    long_description_content_type="text/markdown",
    url="https://github.com/ccwienk/containerregistry",
    packages=setuptools.find_packages(),
    install_requires=[
        'httplib2 >=0.11.3',
        'six>=1.9',
        'oauth2client>=4.0',
        'futures>=3.1.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

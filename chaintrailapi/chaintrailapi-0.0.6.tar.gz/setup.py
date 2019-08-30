import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chaintrailapi",
    version="0.0.6",
    author="University of Notre Dame, Center for Research Computing",
    author_email="CRCsupport@nd.edu",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crcresearch/chaintrailapi",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'pandas', 'sklearn', 'matplotlib', 'requests-toolbelt'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
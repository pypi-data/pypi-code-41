from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="revops",
    version="0.0.6",
    author="Adam Ballai",
    author_email="adam@revops.io",
    description="RevOps Python Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/revops-io/revops-python",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=['requests', 'marshmallow'],
    download_url = 'https://github.com/revops-io/revops-python/archive/v0.0.6.tar.gz',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

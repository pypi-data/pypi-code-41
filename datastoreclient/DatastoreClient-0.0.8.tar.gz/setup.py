import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DatastoreClient",
    version="0.0.8",
    author="TaylorHere",
    author_email="taylorherelee@gmail.com",
    description="Python Client for Datastore APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TaylorHere",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["graphqlclient", "minio", "jinja2", "tqdm", "psutil"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

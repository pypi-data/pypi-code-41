import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seeq",
    version="0.0.41",
    author="Seeq Corporation",
    author_email="support@seeq.com",
    description="The Seeq SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.seeq.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'certifi',
        'ipython',
        'matplotlib',
        'numpy',
        'pandas',
        'six',
        'urllib3'
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)

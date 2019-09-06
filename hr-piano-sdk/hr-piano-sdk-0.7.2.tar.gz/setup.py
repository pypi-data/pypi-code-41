import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hr-piano-sdk",
    version="0.7.2",
    author="Ramiro Rinaldi",
    author_email="dev@hideawayreport.com",
    description="A piano API implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrew-harper/piano_sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'inflect',
        'requests',
        'pycrypto',
    ],
)

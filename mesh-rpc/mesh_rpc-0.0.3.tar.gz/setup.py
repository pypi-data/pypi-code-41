import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mesh_rpc",
    version="0.0.3",
    author="Abhishek Upperwal",
    author_email="mesh@soket.in",
    description="RPC library for mesh-pravah",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pravahio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datetime3",
    version="3.8.0",
    author="packaged by Oren Tirosh",
    author_email="orent@hishome.net",
    description="Latest Python 3.x datetime module packaged for use on older Python",
    long_description=long_description,
    url="https://github.com/orent/datetime3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)


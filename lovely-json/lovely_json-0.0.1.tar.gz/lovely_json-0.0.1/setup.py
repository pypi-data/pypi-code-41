import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lovely_json",
    version="0.0.1",
    author="ccppoo",
    author_email="shmishmi79@gmail.com",
    description="Make Your Json Lovely",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccppoo/lovely_json",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

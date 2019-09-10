import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simutil",
    version="0.0.1",
    author="jeanku, liubing",
    author_email="",
    description="A simple mysql orm base on pymysql",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=["simutil"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'configparser',
    ],
    keywords='util',
    python_requires='>=3',
)
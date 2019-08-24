import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="empire-erp",
    version="0.0.1",
    author="Vladimir Nomkhoev",
    author_email="author@example.com",
    description="Empire ERP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nomhoi/empire-erp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
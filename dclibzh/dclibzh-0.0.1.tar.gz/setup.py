import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dclibzh",
    version="0.0.1",
    author="Francis",
    author_email="jundayan39@Gmail.com",
    description="数字火币交易平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/dadafrancis/dclibzh",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

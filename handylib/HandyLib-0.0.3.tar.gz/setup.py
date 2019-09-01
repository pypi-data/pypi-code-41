import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HandyLib",
    version="0.0.3",
    author="QY-Y",
    author_email="QY-Y@qq.com",
    description="A Handy Library for Everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QY-Y/HandyLib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: Microsoft :: Windows :: Windows 10',
    ],
)
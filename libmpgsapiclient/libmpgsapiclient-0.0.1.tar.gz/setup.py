import setuptools

install_requires = ['requests', 'libenum']

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libmpgsapiclient",
    version="0.0.1",
    author="jiao.xue",
    author_email="jiao.xuejiao@gmail.com",
    description="MPGS API client tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caser789/libmpgsapiclient",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

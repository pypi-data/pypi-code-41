import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="cloudframe",
    version="0.0.1",
    description="A light set of supporting modules to assist the data science workflow based on Cloudframe's proprietary data science enablers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudframe/cloudframe",
    author="Cloudframe Analytics",
    author_email="info@cloudframe.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["model_tracker"],
    include_package_data=True,
    install_requires=["json", "pickle", "pyyaml"]
)
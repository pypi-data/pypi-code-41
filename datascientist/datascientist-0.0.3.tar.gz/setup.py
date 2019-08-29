import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="datascientist",
    version="0.0.3",
    description="A light set of enabling convenience functions based on Cloudframe's proprietary data science enablers.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudframe/datascientist",
    author="Cloudframe Analytics",
    author_email="info@cloudframe.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["datascientist"],
    include_package_data=True,
    install_requires=["pandas", "cx-Oracle", "mysql-connector", "psycopg2"]
)

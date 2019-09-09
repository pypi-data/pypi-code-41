import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="slalom-dataops",
    version="0.1.3",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    license="MIT",
    description="Slalom GGP libary for DataOps automation",
    long_description=README,
    long_description_content_type="text/markdown",
    author="AJ Steers",
    author_email="aj.steers@slalom.com",
    url="https://bitbucket.org/slalom-consulting/propensity_to_buy/src/master/src/",
    download_url="https://github.com/slalom-ggp/dataops/archive/v_0.1.tar.gz",
    keywords=["DATAOPS", "SLALOM", "DATA", "AUTOMATION", "CI/CD", "DEVOPS"],
    install_requires=[
        "awscli",
        "azure-common",
        "azure-datalake-store",
        "boto3",
        # "dataclasses",
        "fire",
        "joblib",
        # "junit-xml",
        # "matplotlib",
        "pandas",
        "psutil",
        "pyspark",
        "s3fs",
        # "xmlrunner",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)

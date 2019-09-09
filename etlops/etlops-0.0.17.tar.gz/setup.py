import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="etlops",
    version="0.0.17",
    author="Carlos Valderrama Montes",
    author_email="carlosvalde9@gmail.com",
    description="ETL Operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'pandas==0.24.2',
        'SQLAlchemy==1.3.5',
        'snowflake-connector-python==1.8.4',
        'snowflake-sqlalchemy==1.1.13',
        'mysql-connector-python==8.0.16',
        'retrying==1.3.3'
    ]
)

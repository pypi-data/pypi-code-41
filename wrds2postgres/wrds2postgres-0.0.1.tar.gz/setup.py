import setuptools

with open("README.md", "r") as f:
    long_description = f.read()
    print(long_description)

setuptools.setup(
    name="wrds2postgres",
    version="0.0.1",
    author="Xiaowen Zhang",
    author_email="seanxwzhang@gmail.com",
    description="Import WRDS tables or SAS data into PostgreSQL. Forked from https://github.com/iangow/wrds2pg.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanxwzhang/wrds2pg/",
    packages=setuptools.find_packages(),
    install_requires=['pandas', 'sqlalchemy', 'paramiko'],
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import os.path
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r") as fh:
    requirements = [line.strip() for line in fh.readlines()]

setuptools.setup(
    author="David Wolinsky",
    author_email="isaac.wolinsky@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description="A Libra client library",
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="librapy",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    url="https://github.com/davidiw/librapy",
    version="0.0.1",
)

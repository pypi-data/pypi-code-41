from os import path

from setuptools import setup


def load_long_descriprion():
    this_directory = path.dirname(path.abspath(__file__))
    with open(path.join(this_directory, "README.rst")) as readme:
        return readme.read()


setup(
    name="py-arduino-api",
    version="0.1",
    url="https://github.com/mmEissen/py-arduino-builder",
    author="Moritz Eissenhauer",
    author_email="moritz.eissenhauer@gmail.com",
    description="",
    packages=["py_arduino_builder"],
    install_requires=["wget"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=load_long_descriprion(),
    long_description_content_type="text/x-rst",
)

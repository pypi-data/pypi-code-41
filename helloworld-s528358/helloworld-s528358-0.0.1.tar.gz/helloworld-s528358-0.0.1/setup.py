from setuptools import setup

with open ("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "helloworld-s528358",
    version = "0.0.1",
    description= "say hello buddy",
    py_modules= "helloworld",
    package_dir= {"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description= long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pypa/twine/issues/372",
    author="ashish",
    author_email="ashish.turbobit@gmail.com",

)
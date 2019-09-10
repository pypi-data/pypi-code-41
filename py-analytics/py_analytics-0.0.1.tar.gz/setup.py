import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="py_analytics",
    version="0.0.1",
    author="Alvaro Brandon",
    author_email="alvaro.brandon@kapsch.net",
    description="A wrapper for the Analytics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gde.kapschtraffic.com/brandon/py_analytics_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="web_crawling",
    version="0.0.1",
    author="Deepsikha Roy",
    author_email="iamdeepsikha2012@gmail.com",
    description="generate climate forecasts using place",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deepsikha97/WeatherWebCrawling",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
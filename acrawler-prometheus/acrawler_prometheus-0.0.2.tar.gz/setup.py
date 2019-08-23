from setuptools import setup


NAME = "acrawler_prometheus"
DESCRIPTION = "The handler working with aCrawler and Prometheus"
URL = "https://github.com/wooddance/acrawler-prometheus"
EMAIL = "zireael.me@gmail.com"
AUTHOR = "wooddance"
VERSION = "0.0.2"
REQUIRED = ["prometheus_client", "acrawler"]


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=">=3.6.0",
    install_requires=REQUIRED,
    py_modules=["acrawler_prometheus"],
)

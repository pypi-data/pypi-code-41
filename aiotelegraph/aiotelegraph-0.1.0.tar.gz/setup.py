from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name = "aiotelegraph",
    version = "0.1.0",
    
    author = "Oleg Yurchik",
    author_email = "oleg.yurchik@protonmail.com",
    url = "https://github.com/OlegYurchik/aiotelegraph",
    
    description = "",
    long_description = open(join(dirname(__file__), "README.md")).read(),
    long_description_content_type = "text/markdown",
    
    packages = find_packages(),
    install_requires = ["aiohttp"],
)

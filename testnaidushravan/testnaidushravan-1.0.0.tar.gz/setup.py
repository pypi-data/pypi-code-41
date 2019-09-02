import pathlib
from setuptools import setup

setup(
    name="testnaidushravan",
    version="1.0.0",
    description="Read the latest Real Python tutorials",
    long_description="Read the latest Real Python tutorials",
    author="Shravan Naidu",
    author_email="shravan.jnaidu@yahoo.com",
    license="MIT",
    scripts=['testnaidushravan.py'],
    include_package_data=True,
    install_requires=["feedparser", "html2text"]
)
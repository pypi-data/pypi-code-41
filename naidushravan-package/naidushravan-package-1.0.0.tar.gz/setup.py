import pathlib
from setuptools import setup

setup(
    name="naidushravan-package",
    version="1.0.0",
    description="Read the latest Real Python tutorials",
    long_description="Read the latest Real Python tutorials",
    author="Shravan Naidu",
    author_email="shravan.jnaidu@yahoo.com",
    license="MIT",
    packages=["shravan_package"],
    include_package_data=True,
    install_requires=["feedparser", "html2text"]
)
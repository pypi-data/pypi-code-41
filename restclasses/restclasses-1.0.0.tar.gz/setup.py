from setuptools import setup, find_packages
from pathlib import Path

setup(
    name = "restclasses",
    version = "1.0.0",
    author = "Forrest Button",
    author_email = "forrest.button@gmail.com",
    description = "library for binding classes to HTTP APIs",
    long_description = Path("README.md").read_text(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/Waffles32/restclasses",
    packages = ['restclasses'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	include_package_data = False,
	install_requires = Path('requirements.txt').read_text().splitlines(),
	python_requires='>3.6',
	zip_safe = True,
)

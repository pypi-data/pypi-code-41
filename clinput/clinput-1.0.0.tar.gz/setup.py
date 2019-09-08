from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="clinput",
    version="1.0.0",
    description="Useful command line input functions with error checking.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cameronmccormack/clinput",
    author="Cameron McCormack",
    author_email="cam.mac@live.co.uk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="command line input",
    packages=["clinput"],
    python_requires=">=3.5",
    install_requires=[],
    extras_require={
        "test": ["pytest"]
    },
    project_urls={
        "Bug Reports": "https://github.com/cameronmccormack/clinput/issues",
        "Source": "https://github.com/cameronmccormack/clinput"
    }
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfathom",
    version="0.0.1",
    author="Jeremy Orme",
    author_email="me@jeremyorme.com",
    description="Text comprehension library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeremyorme/pyfathom",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
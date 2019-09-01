import setuptools

with open("README.md", "rb") as fh:
    long_description = fh.read().decode('utf-8')

setuptools.setup(
    name="packel",
    version="1.0.1",
    author="kiwec",
    author_email="c.wolf@kiwec.net",
    description="Packet serialization/deserialization in a Pythonic way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiwec/packel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

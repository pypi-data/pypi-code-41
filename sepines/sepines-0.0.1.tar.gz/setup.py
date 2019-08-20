import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sepines",
    version="0.0.1",
    author="Rafael Rayes",
    author_email="rafa@rayes.com.br",
    description="This package lets you separate text in lines",
    long_description="""
Use 
```
max_words(text, lines)
```
To separate text in number of words.

And:
```
max_chars(text, lines)
```
to separate text in number of characters
""",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


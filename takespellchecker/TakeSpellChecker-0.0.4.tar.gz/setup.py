import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()	
	
setuptools.setup(
    name="TakeSpellChecker",
    version="0.0.4",
    author="Karina Tiemi Kato",
    author_email="karinatkato@gmail.com",
    description="Machine learning spell check package that combines word's context with characters similarity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karinatk/TakeSpellChecker",
    packages=setuptools.find_packages(),
	install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
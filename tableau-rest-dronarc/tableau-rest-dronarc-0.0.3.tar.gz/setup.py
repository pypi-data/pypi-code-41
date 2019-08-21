import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tableau-rest-dronarc",
    version="0.0.3",
    author="Sam Holmes",
    author_email="dronarc@gmail.com",
    description="A object oreintated approach to Tableau REST interaction. Built to be as generic and modular as possible whilst automating Tableau Server Admin activities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sam-Holmes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
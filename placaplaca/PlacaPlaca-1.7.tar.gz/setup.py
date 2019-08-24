import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PlacaPlaca",
    version="1.7",
    author="Luijo",
    author_email="luijo0319@gmail.com",
    description="Identificador de placas de Panama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VvLuijovV/Placas",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
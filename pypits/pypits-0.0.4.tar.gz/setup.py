import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypits",
    version="0.0.4",
    author="Caian Benedicto",
    author_email="caian@ggaunicamp.com",
    description="The reference python implementation of the SPITS programming model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpg-cepetro/pypits",
    packages=setuptools.find_packages(),
    scripts=[
        'bin/pypits-examples',
        'bin/pypits-gen-api',
        'bin/pypits-jm',
        'bin/pypits-tm'
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.6',
)

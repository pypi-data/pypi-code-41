import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spitz",
    version="0.0.1",
    author="Caian Benedicto",
    author_email="caian@ggaunicamp.com",
    description="The reference python implementation of the SPITS programming model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpg-cepetro/spitz",
    packages=setuptools.find_packages(),
    scripts=[
        'bin/spitz-examples',
        'bin/spitz-gen-api',
        'bin/spitz-jm',
        'bin/spitz-tm'
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.6',
)

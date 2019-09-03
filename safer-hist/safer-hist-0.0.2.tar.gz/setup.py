import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="safer-hist",
    version="0.0.2",
    author="Olivier Dalle",
    author_email="olivier@safer-storage.com",
    description="A system level API to query and manage the SAFER-STORAGE backup and storage in space in time dimensions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.safer-storage.com/safer-dev-priv/nas-histo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
)
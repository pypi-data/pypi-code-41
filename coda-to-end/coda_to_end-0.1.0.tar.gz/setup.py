import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coda_to_end",
    version="0.1.0",
    author="Sean Lamont",
    author_email="sean.a.lamont@outlook.com",
    description="A collection of ML algorithms for Compositional Data Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sean-lamont/coda-to-end",
    install_requires=[
   'numpy'
   ],
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
)

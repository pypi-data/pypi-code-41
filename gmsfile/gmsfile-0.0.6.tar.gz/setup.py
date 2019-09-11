import setuptools

with open("README.md", "r") as fh:
    long_description=fh.read()

setuptools.setup(
        name="gmsfile",
        version="0.0.6",
        author="Gourab Kanti Das",
        author_email="gourabkanti.das@visva-bharati.ac.in",
        description="A converter from XYZ to GAMESS file",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/drylab/gmsfile",
        packages = setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=2.7',
)

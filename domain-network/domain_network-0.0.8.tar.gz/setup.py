import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="domain_network",
    version="0.0.8",
    author="Research-IT support",
    author_email="p.zahedi@uu.nl",
    description="Makes a network out of a URLs in a dataset of tweets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.science.uu.nl/research-it-support/domain_network",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
install_requires=[
        'numpy',
        'pandas'
    ]
)
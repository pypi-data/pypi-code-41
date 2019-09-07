import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="promindset-tools",
    version="0.0.12",
    author="Asaad Najjar",
    author_email="rajjix@rajjix.com",
    description="some useful tools to use here and there.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/promindset/promindset-tools/issues/",
        "Source Code": "https://github.com/promindset/promindset-tools/"
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

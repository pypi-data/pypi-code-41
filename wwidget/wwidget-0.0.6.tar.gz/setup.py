import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wwidget",
    version="0.0.6",
    author="Phearaeun",
    author_email="siphearaeun@gmail.com",
    description="A package to fast embed HTML snippets to any websites or applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pelprek.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
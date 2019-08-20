import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="soio",
    version="0.0.3",
    author="Zhenwei Zhu",
    author_email="zhuzhenwei95@gmail.com",
    description="A single objective intelligent optimization package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zzw95/SOIO",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ignis",
    version="0.0.4",
    author="Teodor Scorpan",
    author_email="teodor.scorpan@gmail.com",
    description="Intuitive library for training neural nets in PyTorch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Catastropha/ignis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

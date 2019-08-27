import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graph_articulations",
    version="0.0.1",
    author="Hameed Abdul",
    author_email="author@example.com",
    description="Extension of PyTorch Geometric and Open 3d for learning kinematic articulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hammania689/graph_articulations",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
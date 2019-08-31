import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="klisch",
    version="0.2.0",
    author="leVirve Salas",
    author_email="gae.m.project@gmail.com",
    description="A cli-integrate config system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leVirve/klisch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["yacs"],
)

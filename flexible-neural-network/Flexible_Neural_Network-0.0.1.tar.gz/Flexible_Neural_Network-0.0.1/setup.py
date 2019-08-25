import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Flexible_Neural_Network",
    version="0.0.1",
    author="Mohamed Abdou",
    author_email="matex512@gmail.com",
    description="A simple and flexible python library that allows you to build custom Neural Networks where you can easily tweak parameters to change how your network behaves",
    url="https://github.com/Mohamed-512/Flexible_Neural_Net",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
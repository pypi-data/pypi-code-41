import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BunalabPy",
    version="0.2",
    author="blueboxdev",
    author_email="thanakorn.vsalab@gmail.com",
    description="A package Bunalab-System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bluebox-dev/Bunalab_Platform/tree/master/BunalabPython",
    packages=setuptools.find_packages(),
    install_requires=[
          'paho-mqtt',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imrepltool",
    version="0.1.5",
    author="GuardianAngel",
    author_email="zhling2012@live.com",
    description="check the image contains the specified image template and set to cover it up",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuardianGH/imrepltool/tree/master/imrepltool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "decorator>=4.4.0",
        "imageio>=2.5.0",
        "matplotlib>=3.1.1",
        "numpy>=1.17.0",
        "Pillow>=6.1.0",
        "PyMySQL>=0.9.3",
        "SQLAlchemy>=1.3.7",
        "requests>=2.22.0",
        "tqdm>=4.32.1",
        "scikit-image==0.15.0",
    ]
)
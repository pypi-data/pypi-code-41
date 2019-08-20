import setuptools

# read the contents of your README file
with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="dlai",
    version="0.0.9",
    author="Laura Lu",
    author_email="new4spam@gmail.com",
    description="DL & ML helper library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    download_url="",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "Pillow",
        "matplotlib",
        "tensorflow-gpu==2.0.0-beta1",
        "seaborn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

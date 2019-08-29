from setuptools import setup, find_packages

with open("README.md") as f:
    longDesc = f.read()


setup(
    name="balautil",
    version="0.1.2",
    author="Bala Prasanna",
    author_email="balaprasannav2009@gmail.com",
    description="A Common machine learning util Collection package",
    long_description=longDesc,
    long_description_content_type="text/markdown",
    url="https://github.com/balaprasanna/balautil",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "plotly",
        "fastai"
    ],
)

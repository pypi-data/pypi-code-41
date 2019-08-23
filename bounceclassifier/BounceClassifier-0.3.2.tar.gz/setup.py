import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BounceClassifier",
    version="0.3.2",
    author="Zhang Wei",
    author_email="zhangw1.2011@gmail.com",
    description="Classify email content by key-word mapping",
    url="https://github.com/Weizhang2017/Email-tools/tree/master/Bounce_classifier",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


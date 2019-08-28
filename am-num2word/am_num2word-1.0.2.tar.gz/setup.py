import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="am_num2word",
    version="1.0.2",
    author="Mitiku Yohannes",
    author_email="se.mitiku.yohannes@gmail.com",
    description="Number to Amharic words representation package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mitiku1/AmharicNumber2Word",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

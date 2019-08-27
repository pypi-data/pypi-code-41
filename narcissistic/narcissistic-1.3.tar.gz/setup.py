import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="narcissistic",
    version="1.3",
    author="DorcasYang",
    author_email="dorcasyangyijing@163.com",
    description="check if a number is narcissistic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DorcasYang/narcissistic/tree/master/narcissistic",
    packages=['narcissistic'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

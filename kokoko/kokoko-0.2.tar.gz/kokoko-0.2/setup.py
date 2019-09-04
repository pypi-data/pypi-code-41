import setuptools

with open ("README.md", "r") as fn:
        long_description = fn.read()

setuptools.setup(
    name = "kokoko",
    version= "0.2",
    scripts=["kokoko"],
    author="wk-j",
    author_email="somnuk.wk@gmail.com",
    description="Test package",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wk-j",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
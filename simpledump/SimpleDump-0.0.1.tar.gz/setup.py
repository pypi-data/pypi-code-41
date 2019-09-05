import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SimpleDump",
    version="0.0.1",
    author="Vladimir Udartsev",
    author_email="v.udartsev@gmail.com",
    description="dump functions for debugging Pythone code in PHP-style",
    long_description="When debugging in Python, ypu can frequently find it useful to simply stick a var_dump() in code to show what a variable is, what it`s value is, and the same for anything that it contains.",
    long_description_content_type="text/markdown",
    url="https://github.com/udartsev/SimpleDump.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)

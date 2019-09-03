import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeslicer",
    version="1.3.0",
    author="Nicholas Ramkissoon",
    description="Package for creating timeslice images from time lapses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nramkissoon/Time-Slice",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
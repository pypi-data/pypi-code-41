import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cornea",
    version="0.0.1",
    author="Praveen Ravichandran",
    author_email="pravinba9495@gmail.com",
    description="A PyPI package to extract insightful information about an image using Machine Intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pravinba9495/cornea",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    python_requires="~=3.7",
    license="MIT"
)

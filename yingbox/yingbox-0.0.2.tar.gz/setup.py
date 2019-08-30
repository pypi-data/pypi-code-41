import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yingbox",
    version="0.0.2",
    author="Ying Zhou",
    author_email="yingzhou474@gmail.com",
    description="Ying's data science helper functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathyingzhou/yingbox",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pandas','copy','pymongo','pickle', 'scikit-learn']
)

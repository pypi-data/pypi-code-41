import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="compare-versions-s528358",
    version="0.0.1.post2",
    author="Ashish Jamuda",
    py_modules=["compareVersions"],
    package_dir={'':'src'},
    author_email="ashish.turbobit@gmail.com",
    description="script to compare versions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashishiit/Ashish_Jamuda_test/tree/master/Problem%20B",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
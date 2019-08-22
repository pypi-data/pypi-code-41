import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gorpyter",
    version="0.6.1",
    author="Layne Sadler",
    author_email="layne.sadler@gmail.com",
    description="Python wrapper for GOR's R SDK with Pandas serialization.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/gorpyter/",
    license="WXNC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'rpy2>=3.0.5','tzlocal>=2.0.0', 'pandas>=0.25.0', 'numpy>=1.17.0',
    ],
)
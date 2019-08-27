import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="distribute_config",
    version="0.1.5",
    author="Sébastien IOOSS",
    author_email="archimist.linux@gmail.com",
    description="A package to handle multi-source distributed configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Net-Mist/distribute_config",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite="nose.collector",
    tests_require=['nose'],
    install_requires=[
        'PyYAML',
    ],
)

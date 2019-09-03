import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='convizit',
    version='0.3.7',
    scripts=['convizit_pkg'],
    author="Convizit",
    author_email="convizit@gmail.com",
    description="Convizit database access package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Convizit/python-plugin",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    package_dir={'convizit': 'convizit'},
    package_data={'convizit': ['config.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

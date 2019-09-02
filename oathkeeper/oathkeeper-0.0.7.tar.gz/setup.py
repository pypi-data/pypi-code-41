import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oathkeeper",
    version="0.0.7",
    author="yashvardhan srivastava",
    author_email="yash@greendeck.com",
    description="Oathkeeper Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greendeck",
    packages=['oathkeeper', 'oathkeeper.src', 'oathkeeper.src.oathkeeper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=False
)

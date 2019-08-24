import setuptools

VERSION = '0.0.13'

with open("pip.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="delineate-io",
    version=VERSION,
    py_modules=['app'],
    author="https://www.delineate.io",
    author_email="oss@delineate.io",
    description="Utility for the current environment versions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/delineateio/delineateio.tools",
    download_url='https://github.com/delineateio/delineateio.tools/tarball/{}'.format(VERSION),
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['delineate-io=app:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
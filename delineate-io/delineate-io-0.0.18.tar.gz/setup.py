import setuptools

VERSION = '0.0.18'

with open("pip.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="delineate-io",
    version=VERSION,
    py_modules=['console'],
    author="https://www.delineate.io",
    author_email="oss@delineate.io",
    description="Tools to simplify the management of local environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/delineateio/delineateio.tools",
    download_url='https://github.com/delineateio/delineateio.tools/tarball/{}'.format(VERSION),
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'click==7.0',
        'PrettyTable==0.7.2',
        'termcolor==1.1.0'
    ],
    entry_points={
        'console_scripts': ['delineate-io=console:cli'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
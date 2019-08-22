import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="log_ip",
    version="0.0.1",
    author="FrenchCommando",
    author_email="martialren@gmail.com",
    description="A script that dumps your IP into a log file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrenchCommando/log_ip",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['log-ip=log_ip.log_ip:main'],
    }
)

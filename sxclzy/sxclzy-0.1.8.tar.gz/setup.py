import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sxclzy",
    version="0.1.8",
    author="GuardianAngel",
    author_email="zhling2012@live.com",
    description="a tool to schedule your functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuardianGH/sxclzy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'psutil>=5.6.2',
        'prettytable>=0.7.2',
        'SQLAlchemy>=1.3.3',
        'dill>=0.3.0',
    ]
)
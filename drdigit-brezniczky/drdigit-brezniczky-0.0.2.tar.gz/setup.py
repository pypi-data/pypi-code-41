import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="drdigit-brezniczky",
    version="0.0.2",
    author="Janos Brezniczky",
    author_email="brezniczky@gmail.com",
    description="A digit doctoring detection package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brezniczky/drdigit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning ",
        "Topic :: Scientific/Engineering"
    ],
    install_requires=[
        "joblib>=0.13.2",
        "numpy>=1.17.0",
        "pandas>=0.24.2",
        "python-dateutil>=2.8.0",
        "pytz>=2019.2",
        "scipy>=1.3.1",
        "six>=1.12.0",
    ]
)

from distutils.core import setup

setup(
    # Application name:
    name="micro-kit",

    # Version number (initial):
    version="1.1.3",

    # Application author details:
    author="Chanpreet Singh Chhabra",
    author_email="chanpreet.chhabra@innovaccer.com",

    # Packages
    packages=["micro_kit"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://pypi.org/project/micro-kit/",

    description="A helper kit to power the APIs",

    # Dependent packages (distributions)
    install_requires=[
        "flask",
    ]
)
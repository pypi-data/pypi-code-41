from setuptools import setup

setup(
    # Application name:
    name="ComStats",

    # Version number (initial):
    version="0.2.0",

    # Application author details:
    author="Data Science Team @ Zappistore",
    author_email="datascience@zappistore.com",

    # Packages
    packages=['ComStats'],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://pypi.org/project/ComStats/",
    # license="LICENSE.txt",
    description="Do combinatorial statistics on numpy ndarrays",
    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "numpy",
        "scipy",
    ],
)

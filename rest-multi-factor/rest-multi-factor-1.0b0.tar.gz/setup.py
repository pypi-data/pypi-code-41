"""setup script for rest-multi-factor."""

import os

from setuptools import find_packages, setup


def get_long_description():
    """
    Retrieve the long description from the README.

    :return: The long description
    :rtype: str
    """
    base = os.path.abspath(os.path.dirname(__file__))
    file = open(os.path.join(base, "README.md"))
    data = file.read()

    file.close()
    return data


setup(
    name="rest-multi-factor",

    version=__import__("rest_multi_factor").__version__,
    description="Multi factor for django rest framework",

    long_description=get_long_description(),
    long_description_content_type="text/markdown",

    url="https://github.com/KENTIVO/rest-multi-factor",

    author="Joël Maatkamp",
    author_email="joel.maatkamp@kentivo.com",

    # Not yet available
    license="MIT",

    keywords="",

    zip_safe=False,

    install_requires=[
        "django",
        "djangorestframework",
        "cryptography",
    ],

    extras_require={
        "qr":   ["qrcode", "pillow"],
        "test": ["factory-boy"],
    },

    packages=find_packages(
        exclude=["tests*"],
    ),


    # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",

        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",

        "Programming Language :: Python :: 3 :: Only",

        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.2",

        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",

        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ]
)

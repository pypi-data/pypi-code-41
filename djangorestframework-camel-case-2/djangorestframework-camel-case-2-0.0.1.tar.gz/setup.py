#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open("README.md").read()
import djangorestframework_camel_case

setup(
    name="djangorestframework-camel-case-2",
    version=djangorestframework_camel_case.__version__,
    description="Camel case JSON support for Django REST framework.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Cesar Canassa",
    author_email="cesar.canassa@gmail.com",
    url="https://github.com/canassa/djangorestframework-camel-case",
    packages=["djangorestframework_camel_case"],
    package_dir={"djangorestframework_camel_case": "djangorestframework_camel_case"},
    include_package_data=True,
    install_requires=[],
    extras_require={
        "tests": ["pytest", "flake8", "django", "djangorestframework"]
    },
    license="BSD",
    zip_safe=False,
    keywords="djangorestframework_camel_case",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
)

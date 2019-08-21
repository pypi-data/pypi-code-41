"""
The setup script.
"""
import os

from setuptools import find_packages
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="jsmsgr",
    version="0.0.6",
    description="Django app to make sending transactional messages to Semaphore a breeze!",
    author="Juntos Somos Mais",
    url="https://github.com/juntossomosmais/jsmsgr",
    packages=find_packages(include=["jsmsgr", "jsmsgr.core", "jsmsgr.support"]),
    install_requires=["jsm-user-services>=0.2.0", "django>=1.11", "django-stomp>=0.0.19"],
    # include_package_data=True,
    zip_safe=False,
    test_suite="jsmsgr.tests",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 2.1",
        "Environment :: Web Environment",
        "Natural Language :: Portuguese (Brazilian)",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)

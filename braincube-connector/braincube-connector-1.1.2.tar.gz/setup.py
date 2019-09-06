from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Name of the project, users can install it with this name.
    name="braincube-connector",
    version="1.1.2",
    author="Braincube",
    author_email="io@braincube.com",
    license="The MIT License (MIT)",
    description="Offers an API to retrieve data from the Braincube platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    keywords='bc_connector API braincube',
    # Tags too search the project.
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.4",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ),
    install_requires=['Flask', 'Flask-Cors', 'requests', 'pandas', 'gevent', 'pyOpenSSL'],
    include_package_data=True
)

import os
from setuptools import find_packages, setup
# from io import open

with open(os.path.join(os.path.dirname(__file__), 'readme.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-chart-compare",
    version="1.0.4",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",  # example license
    description="Compare matrices in a django app",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/chasek23/django-chart-compare",
    download_url='https://github.com/chasek23/xml2pandas/archive/0.0.0.tar.gz',
    author="Chase Kelly",
    author_email="chase@microsearch.net",
    install_requires=[
        'pandas',
        'bokeh',
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    project_urls={
        'Documentation': 'https://github.com/chasek23/django-chart-compare',
        'Funding': 'https://microsearch.cloud/',
        'Say Thanks!': 'http://chasekel.ly/',
        'Source': 'https://github.com/chasek23/django-chart-compare',
        'Tracker': 'https://github.com/chasek23/django-chart-compare/issues',
    },
)

# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()


setup(
    name='woohoo-pdns',
    version='2019.1.3',
    description='woohoo pDNS implementation',
    long_description=readme,
    long_description_content_type="text/x-rst",
    author='Andreas Scherrer',
    author_email='andreas@scherrer.io',
    url='https://gitlab.com/scherand/woohoo-pdns',
    project_urls={
        "Bug Tracker": "https://gitlab.com/scherand/woohoo-pdns/issues",
        "Documentation": "https://woohoo-pdns.readthedocs.io",
        "Source Code": "https://gitlab.com/scherand/woohoo-pdns",
    },
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["woohoo_pdns", "woohoo_pdns.api"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pdns = woohoo_pdns.__main__:main",
        ]
    },
    install_requires = [
        "alembic",
        "flask",
        "flask-httpauth",
        "gunicorn",
        "psycopg2-binary",
        "python-dateutil",
        "pyyaml",
        "requests",
        "sphinx",
        "sqlalchemy",
    ]
)

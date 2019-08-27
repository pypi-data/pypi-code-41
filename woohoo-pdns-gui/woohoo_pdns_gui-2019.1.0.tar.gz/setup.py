# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

setup(
    name='woohoo_pdns_gui',
    version='2019.1.0',
    description='Web GUI for pDNS',
    long_description=readme,
    long_description_content_type="text/x-rst",
    author='Andreas Scherrer',
    author_email='andreas@scherrer.io',
    url='https://gitlab.com/scherand/woohoo-pdns-gui',
    project_urls={
        "Bug Tracker": "https://gitlab.com/scherand/woohoo-pdns-gui/issues",
        "Documentation": "https://woohoo-pdns-gui.readthedocs.io",
        "Source Code": "https://gitlab.com/scherand/woohoo-pdns-gui",
    },
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
    ],
    packages=["woohoo_pdns_gui"],
    install_requires=[
        "flask ~= 1.1.1",
        "gunicorn ~= 19.9.0",
        "sphinx ~= 2.1.2",
    ]
)


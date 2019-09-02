# -*- coding: utf-8 -*-

import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyelectrica",
    version="1.1.4-post2",
    author="Isai Aragón P.",
    author_email="isaix25@gmail.com",
    description="Módulo PyElectrica, útil para resolver problemas específicos \
    de Máquinas y Circuitos Eléctricos, así como de Instalaciones Eléctricas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pyelectrica.ml",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'matplotlib', 'scipy', 'SchemDraw'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: Spanish",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.5',
)

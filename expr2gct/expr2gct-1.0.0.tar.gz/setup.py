# -*- coding: utf-8 -*-
from setuptools import setup
from os import path

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='expr2gct',  # Required
    version='1.0.0',  # Required
    description=('generate gct file (version 1.2, for GSEA or ssGSEA) '
                 'from gene expression matrix file'),  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/sxropensource/expr2gct',  # Optional
    author='sxropensource',  # Optional
    author_email='sxropensource@163.com',  # Optional
    classifiers=[
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='GSEA ssGSEA GCT',  # Optional
    py_modules=['expr2gct'],
    entry_points={  # Optional
        'console_scripts': [
            'expr2gct=expr2gct:main',
        ],
    },
)

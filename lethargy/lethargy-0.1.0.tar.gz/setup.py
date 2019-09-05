# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['lethargy']
setup_kwargs = {
    'name': 'lethargy',
    'version': '0.1.0',
    'description': 'A minimal library to make your option-parsing easier.',
    'long_description': None,
    'author': 'SeparateRecords',
    'author_email': 'separaterecords@users.noreply.github.com',
    'url': 'https://github.com/SeparateRecords/lethargy',
    'py_modules': modules,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

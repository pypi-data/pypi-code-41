# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['lethargy']
setup_kwargs = {
    'name': 'lethargy',
    'version': '0.1.1',
    'description': 'A minimal library to make your option-parsing easier.',
    'long_description': '# Lethargy\n\nA little library that provides you with the tools to make your option parsing easy.\n\n(documentation coming soon)\n',
    'author': 'SeparateRecords',
    'author_email': 'me@rob.ac',
    'url': 'https://github.com/SeparateRecords/lethargy',
    'py_modules': modules,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

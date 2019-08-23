# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['crapy']
setup_kwargs = {
    'name': 'crapy',
    'version': '0.0.2',
    'description': '',
    'long_description': None,
    'author': 'jessekrubin',
    'author_email': 'jessekrubin@gmail.com',
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

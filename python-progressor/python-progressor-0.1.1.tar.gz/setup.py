# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['progressor']
install_requires = \
['jsonrpc-requests>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'python-progressor',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Alexander Artemenko',
    'author_email': 'svetlyak.40wt@gmail.com',
    'url': 'https://github.com/40ants/python-progressor',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)

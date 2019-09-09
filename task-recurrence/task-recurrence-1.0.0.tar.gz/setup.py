# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['task_recurrence']
install_requires = \
['arrow>=0.14.7,<0.15.0']

setup_kwargs = {
    'name': 'task-recurrence',
    'version': '1.0.0',
    'description': 'A Recurrence library for todo applications that provide next date calculation and string generation',
    'long_description': None,
    'author': 'BeatLink',
    'author_email': 'beatlink@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

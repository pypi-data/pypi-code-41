# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['presentation_mode']
install_requires = \
['DBussy>=1.2,<2.0', 'python-decouple>=3.1,<4.0', 'slackclient>=2.1,<3.0']

entry_points = \
{'console_scripts': ['presentation_mode = presentation_mode:main']}

setup_kwargs = {
    'name': 'presentation-mode',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Simon Brulhart',
    'author_email': 'simon@brulhart.me',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

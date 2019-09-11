# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['impipes']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.1,<4.0',
 'numpy>=1.17,<2.0',
 'opencv-python>=4.1,<5.0',
 'scipy>=1.3,<2.0',
 'wget>=3.2,<4.0']

setup_kwargs = {
    'name': 'impipes',
    'version': '0.1.8',
    'description': '',
    'long_description': '# Welcome to `impipes`\n\n## About this package\n\n`impipes` is a Python package built to automate the image preprocessing to feed an AI model.\n\n## What was this built for?\n\nThis package was originally developed by [Lukasz Kaczmarek](mailto:lukaszk76@gmail.com), [Cristian Vargas](mailto:rodolfoferroperez@gmail.com), [Ramón Ontiveros](mailto:ramontiveros@gmail.com), and [Rodolfo Ferro](mailto:rodolfoferroperez@gmail.com) as part of the [Tree Identification Challenge with AI](https://medium.com/omdena/building-ai-for-good-by-the-people-for-the-people-d98ad78b5001) at [Omdena](https://omdena.com/).\n\n## Refer to this package\n\n    # We will be providing more info about how to refer\n    # to this Python package.\n    from impipes import pipes\n    ...\n\n_More content will be added soon._',
    'author': 'Rodolfo Ferro',
    'author_email': 'rodolfoferroperez@gmail.com',
    'url': 'https://impipes.rtfd.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

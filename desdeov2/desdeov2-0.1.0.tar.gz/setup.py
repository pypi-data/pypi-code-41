# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['desdeov2',
 'desdeov2.manager',
 'desdeov2.methods',
 'desdeov2.problem',
 'desdeov2.solver',
 'desdeov2.utils']

package_data = \
{'': ['*']}

install_requires = \
['jupyter>=1.0,<2.0',
 'numpy>=1.17,<2.0',
 'plotly>=4.1,<5.0',
 'scipy>=1.3,<2.0',
 'sklearn>=0.0.0,<0.0.1']

setup_kwargs = {
    'name': 'desdeov2',
    'version': '0.1.0',
    'description': 'Rewrite of the original DESDEO framework. Contains traditional MCDM algorithms and scalarization utilities. To be split into multiple modules.',
    'long_description': None,
    'author': 'Giovanni Misitano',
    'author_email': 'gialmisi@student.jyu.fi',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

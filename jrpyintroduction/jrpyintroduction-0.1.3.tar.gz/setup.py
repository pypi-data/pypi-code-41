# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrpyintroduction', 'jrpyintroduction.datasets']

package_data = \
{'': ['*'],
 'jrpyintroduction': ['vignettes/*'],
 'jrpyintroduction.datasets': ['data/*']}

install_requires = \
['matplotlib>=3.1,<4.0', 'numpy>=1.14.4,<2.0.0', 'pandas>=0.20.1,<0.24']

setup_kwargs = {
    'name': 'jrpyintroduction',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Jamie',
    'author_email': 'jamie@jumpingrivers.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

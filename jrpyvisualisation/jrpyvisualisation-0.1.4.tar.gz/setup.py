# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrpyvisualisation', 'jrpyvisualisation.datasets']

package_data = \
{'': ['*'],
 'jrpyvisualisation': ['vignettes/*'],
 'jrpyvisualisation.datasets': ['data/*']}

install_requires = \
['numpy>=1.17,<2.0', 'pandas>=0.25.0,<0.26.0', 'plotly>=4.1,<5.0']

setup_kwargs = {
    'name': 'jrpyvisualisation',
    'version': '0.1.4',
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

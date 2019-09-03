# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['crecs', 'crecs.ds', 'crecs.rs', 'crecs.sage']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17',
 'scikit-learn>=0.19.1',
 'scipy>=0.16',
 'typing_extensions>=3.7,<4.0']

extras_require = \
{'container': ['sagemaker-containers>=2.4,<3.0'],
 'sagemaker': ['sagemaker>=1.18,<2.0']}

setup_kwargs = {
    'name': 'crecs',
    'version': '2019.9.0',
    'description': '',
    'long_description': None,
    'author': 'Germano Gabbianelli',
    'author_email': 'git@germano.dev',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)

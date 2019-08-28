# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dvc_cc_agent']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4,<2.0', 'pyjson>=1.3,<2.0']

entry_points = \
{'console_scripts': ['dvc-cc-agent = dvc_cc_agent.main:main']}

setup_kwargs = {
    'name': 'dvc-cc-agent',
    'version': '0.8.0',
    'description': 'This script is the agent that should only be called in a docker. It executes scripts of github defined with dvc.',
    'long_description': None,
    'author': 'Jonas',
    'author_email': 'jonas.annuscheit@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

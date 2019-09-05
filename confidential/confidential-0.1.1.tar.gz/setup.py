# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['confidential']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['confidential = '
                     'confidential.secrets_manager:decrypt_secret']}

setup_kwargs = {
    'name': 'confidential',
    'version': '0.1.1',
    'description': 'Manage secrets in your projects using AWS Secrets Manager',
    'long_description': None,
    'author': 'Daniel van Flymen',
    'author_email': 'dvf@candidco.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

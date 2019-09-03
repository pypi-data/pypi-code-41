# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_cloud',
 'dophon_cloud.enhance_pkg',
 'dophon_cloud.eureka_client',
 'dophon_cloud.utils']

package_data = \
{'': ['*']}

install_requires = \
['dophon', 'dophon_cloud_center', 'py_eureka_client']

setup_kwargs = {
    'name': 'dophon-cloud',
    'version': '1.0.3',
    'description': 'dophon cloud(import reg center)',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pack']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pyipwhois = entry:main']}

setup_kwargs = {
    'name': 'ip-geolocation-api',
    'version': '1.0.2',
    'description': 'Free IP Geolocation API and IP Location Lookup Database by <a>https://ipwhois.io/</a>',
    'long_description': None,
    'author': 'ipwhois.io',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '==2.7.5',
}


setup(**setup_kwargs)

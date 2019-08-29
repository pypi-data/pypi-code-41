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
    'version': '1.1.1',
    'description': 'Free IP Geolocation API and IP Location Lookup Database by https://ipwhois.io',
    'long_description': '# IP Geolocation API - Python\nA Simple python wrapper for <a href="https://ipwhois.io">IP Geolocation API</a> by ipwhois.io',
    'author': 'ipwhois.io',
    'author_email': None,
    'url': 'https://ipwhois.io/',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '==2.7.5',
}


setup(**setup_kwargs)

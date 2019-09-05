# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['s3pypi']

package_data = \
{'': ['*'], 's3pypi': ['templates/*']}

install_requires = \
['Jinja2>=2.10.1,<3.0.0', 'boto3>=1.9.211,<2.0.0', 'wheel>=0.33.6,<0.34.0']

entry_points = \
{'console_scripts': ['s3pypi = s3pypi.__main__:main']}

setup_kwargs = {
    'name': 's3pypi',
    'version': '0.9.2',
    'description': 'CLI for creating a Python Package Repository in an S3 bucket',
    'long_description': None,
    'author': 'Matteo De Wint',
    'author_email': 'matteo@novemberfive.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['proxy6']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow==3.0.0rc9', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'proxysix',
    'version': '1.0.0a4',
    'description': 'API wrapper for Proxy6',
    'long_description': '# Proxy6 API wrapper\n[![Build status](https://api.travis-ci.com/michaeldel/proxy6.svg?branch=master)](https://travis-ci.com/michaeldel/proxy6)\n[![PyPI - Status](https://img.shields.io/pypi/v/proxysix)](https://pypi.org/project/proxysix/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/proxysix)](https://pypi.org/project/proxysix/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Install\nInstall the `proxysix` package with `pip`:\n```\npip install proxysix\n```\n',
    'author': 'michaeldel',
    'author_email': 'michaeldel@protonmail.com',
    'url': 'https://github.com/michaeldel/proxy6',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

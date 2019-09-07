# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hydrus']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'hydrus-api',
    'version': '1.11.2',
    'description': 'Python module implementing the Hydrus API',
    'long_description': "# Hydrus API\nPython module implementing the Hydrus API.\n\n# Requirements\n- Python 3\n- requests library (`pip install requests`)\n\n# Installation\n`$ pip install hydrus-api`\n\nIf you want to use the package in your own (installable) Python project, specify\nit in your `setup.py` using: `install_requires=['hydrus-api']`.\n\n# Description\nIt is _highly_ recommended that you do not solely rely on the docstrings in this\nmodule to use the API, instead read the official documentation (latest\n[here](https://hydrusnetwork.github.io/hydrus/help/client_api.html)).\n\nWhen instantiating `Client` the `acccess_key` is optional, allowing you to\ninitially manually request permissions using `request_new_permissions()`.\nAlternatively there is `utils.request_api_key()` to make this easier. You can\ninstantiate a new `Client` with the returned access key after that.\n\nIf the API version the module is developed against and the API version at the\nspecified endpoint differ, you will be warned but not prevented from using any\nfunctionality -- this might have unintended consequences, be careful.\n\nIf something with the API goes wrong, a subclass of `APIError`\n(`MissingParameter`, `InsufficientAccess`, `ServerError`) or `APIError` itself\nwill be raised with the [`requests.Response`](http://docs.python-requests.org/en/master/api/#requests.Response)\nobject that caused the error. `APIError` will only be raised directly, if the\nreturned status code is unrecognized.\n\nThe module provides `Permission`, `URLType`, `ImportStatus`, `TagAction`,\n`TagStatus` and `PageType` enums for your convenience. Values in the response\ndata, represented by the enums, are automatically converted -- this makes them\nmore easily readable, the enum values can still be handled like regular\nintegers. Some utility functions are available in `hydrus.utils`.\n\nCheck out `examples/` for some example applications.\n",
    'author': 'cryzed',
    'author_email': 'cryzed@googlemail.com',
    'url': 'https://gitlab.com/cryzed/hydrus-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

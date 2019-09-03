# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pdocs']

package_data = \
{'': ['*'], 'pdocs': ['templates/*']}

install_requires = \
['Mako>=1.1,<2.0', 'Markdown>=3.0.0,<4.0.0', 'hug>=2.6,<3.0']

entry_points = \
{'console_scripts': ['pdocs = pdocs.cli:__hug__.cli']}

setup_kwargs = {
    'name': 'pdocs',
    'version': '1.0.0',
    'description': 'A simple program and library to auto generate API documentation for Python modules.',
    'long_description': "[![pdocs - Documentation Powered by Your Python Code.](https://raw.github.com/timothycrosley/pdocs/master/art/logo_large.png)](https://timothycrosley.github.io/pdocs/)\n_________________\n\n[![PyPI version](https://badge.fury.io/py/pdocs.svg)](http://badge.fury.io/py/pdocs)\n[![Build Status](https://travis-ci.org/timothycrosley/pdocs.svg?branch=master)](https://travis-ci.org/timothycrosley/pdocs)\n[![codecov](https://codecov.io/gh/timothycrosley/pdocs/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/pdocs)\n[![Join the chat at https://gitter.im/pdocs/community](https://badges.gitter.im/pdocs/community.svg)](https://gitter.im/pdocs/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/pdocs/)\n[![Downloads](https://pepy.tech/badge/pdocs)](https://pepy.tech/project/pdocs)\n_________________\n\n[Read Latest Documentation](https://timothycrosley.github.io/pdocs/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/pdocs/)\n_________________\n\n\n`pdocs` is a library and a command line program to discover the public\ninterface of a Python module or package. The `pdocs` script can be used to\ngenerate Markdown or HTML of a module's public interface, or it can be used\nto run an HTTP server that serves generated HTML for installed modules.\n\n`pdocs` is an MIT Licensed fork of `pdoc` with the goal of staying true to the original vision\nlayed out by the projects creator.\n\nNOTE: For most projects, the best way to use `pdocs` is using [portray](https://timothycrosley.github.io/portray/).\n\n[![asciicast](https://asciinema.org/a/265744.svg)](https://asciinema.org/a/265744)\n\nFeatures\n--------\n\n* Support for documenting data representation by traversing the abstract syntax\n  to find docstrings for module, class and instance variables.\n* For cases where docstrings aren't appropriate (like a\n  [namedtuple](http://docs.python.org/2.7/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields)),\n  the special variable `__pdocs__` can be used in your module to\n  document any identifier in your public interface.\n* Usage is simple. Just write your documentation as Markdown. There are no\n  added special syntax rules.\n* `pdocs` respects your `__all__` variable when present.\n* `pdocs` will automatically link identifiers in your docstrings to its\n  corresponding documentation.\n* When `pdocs` is run as an HTTP server, external linking is supported between\n  packages.\n* The `pdocs` HTTP server will cache generated documentation and automatically\n  regenerate it if the source code has been updated.\n* When available, source code for modules, functions and classes can be viewed\n  in the HTML documentation.\n* Inheritance is used when possible to infer docstrings for class members.\n\nThe above features are explained in more detail in pdocs's documentation.\n\n`pdocs` is compatible with Python 3.6 and newer.\n\n",
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

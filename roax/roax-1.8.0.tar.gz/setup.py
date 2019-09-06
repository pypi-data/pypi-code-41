# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['roax']

package_data = \
{'': ['*']}

install_requires = \
['WebOb>=1.8,<2.0', 'isodate>=0.6,<0.7', 'wrapt>=1.11,<2.0']

setup_kwargs = {
    'name': 'roax',
    'version': '1.8.0',
    'description': 'Lightweight framework for building resource-oriented applications.',
    'long_description': '# Roax\n\n[![PyPI](https://badge.fury.io/py/roax.svg)](https://badge.fury.io/py/roax)\n[![License](https://img.shields.io/github/license/roax/roax.svg)](https://github.com/roax/roax/blob/master/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-master-blue.svg)](https://github.com/roax/roax/)\n[![Travis CI](https://travis-ci.org/roax/roax.svg?branch=master)](https://travis-ci.org/roax/roax)\n[![Codecov](https://codecov.io/gh/roax/roax/branch/master/graph/badge.svg)](https://codecov.io/gh/roax/roax)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nRo·ax /ˈɹoʊ.æks/  \nA lightweight Python resource-oriented framework. \n\n## Introduction\n\nRoax is a lightweight framework for building resource-oriented applications in Python.\nBy composing your application as a set of resources that expose operations through a uniform\ninterface, they can be automatically exposed through a REST and/or command line interface.\n\n## Features\n\n* Resource operations accessed through WSGI based REST API.\n* Command-line interface to resource operations.\n* Generates [OpenAPI](https://www.openapis.org/) interface description, compatible with [Swagger UI](https://swagger.io/tools/swagger-ui/).\n* Schema enforcement of resource operation parameters and return values.\n* Authorization to resource operations enforced through imperative security policies.\n\n## Quick start\n\n### Installation\n\n```\npip install roax\n```\n\n### Hello world\n\nHere is a minimal application that responds with `"Hello world!"` when the\nclient accesses [http://localhost:8000/hello](http://localhost:8000/hello).\n\n```python\nimport roax.schema as schema\n\nfrom roax.resource import Resource, operation\nfrom roax.wsgi import App\nfrom wsgiref.simple_server import make_server\n\nclass HelloResource(Resource):\n\n    @operation(returns=schema.str(), security=[])\n    def read(self):\n        return "Hello world!"\n\napp = App("/", "Hello", "1.0")\napp.register_resource("/hello", HelloResource())\n\nif __name__== "__main__":\n    make_server("", 8000, app).serve_forever()\n```\n',
    'author': 'Paul Bryan',
    'author_email': 'pbryan@anode.ca',
    'url': 'https://github.com/roax/roax/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

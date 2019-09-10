# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['examples']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=0.32.2,<0.33.0']

setup_kwargs = {
    'name': 'examples',
    'version': '0.1.1',
    'description': 'Tests and Documentation Done by Example.',
    'long_description': "[![eXamples - Python Tests and Documentation Done by Example.](https://raw.github.com/timothycrosley/examples/master/art/logo_large.png)](https://timothycrosley.github.io/examples/)\n_________________\n\n[![PyPI version](https://badge.fury.io/py/examples.svg)](http://badge.fury.io/py/examples)\n[![Build Status](https://travis-ci.org/timothycrosley/examples.svg?branch=master)](https://travis-ci.org/timothycrosley/examples)\n[![codecov](https://codecov.io/gh/timothycrosley/examples/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/examples)\n[![Join the chat at https://gitter.im/timothycrosley/examples](https://badges.gitter.im/timothycrosley/examples.svg)](https://gitter.im/timothycrosley/examples?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/examples/)\n[![Downloads](https://pepy.tech/badge/examples)](https://pepy.tech/project/examples)\n_________________\n\n[Read Latest Documentation](https://timothycrosley.github.io/examples/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/examples/)\n_________________\n\n**eXamples** (AKA: xamples for SEO purposes) is a Python3 library enabling interactable, self-documentating, and self-verifying examples to be attached to Python functions using decorators.\n\nKey Features:\n\n* **Simple and Obvious API**: Simply add `@examples.example(*args, **kwargs)` decorators for each example you want to add to a function.\n* **Auto Documenting**: Examples, by default, get added to your functions docstring viewable both in interactive interpreters and when using examples or pdocs.\n* **Signature Validating**: All examples can easily be checked to ensure they match the function signature (and type annotations!) with a single call (`examples.verify_all_signatures()`).\n* **Act as Tests**: Examples act as additional test cases, that can easily be verified using a single test case in your favorite test runner: (`examples.test_all_examples()`).\n\nWhat's Missing:\n\n* **Class Support**: Currently examples can only be attached to individual functions. Class and method support is planned for a future release.\n\n## Quick Start\n\nThe following guides should get you up and running with a documentation website in no time.\n\n1. Install: `pip3 install examples`\n2. Add Examples:\n\n        from examples import example\n\n        @example(1, 1, _example_returns=2)\n        def add(number_1: int, number_2: int) -> int:\n            return number_1 + number_2\n\n3. Verify and test examples\n\n        import examples\n\n        examples.verify_and_test_all_examples()\n\n4. Introspect examples\n\n        import examples\n\n        examples.get(add)[0].use() == 2\n\n## Why Create Examples?\n\nI've always wanted a way to attach examples to functions in a way that would be re-useable for documentation, testing, and API proposes.\nJust like moving Python parameter types from comments into prorammatically specified and easily introspectable entities has made them more braodly useful,\nI hope examples can do the same for example parameters.\n\nI hope you too find `eXamples` useful!\n\n~Timothy Crosley\n",
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

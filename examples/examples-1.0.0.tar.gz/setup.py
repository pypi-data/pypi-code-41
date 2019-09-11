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
    'version': '1.0.0',
    'description': 'Tests and Documentation Done by Example.',
    'long_description': "[![eXamples - Python Tests and Documentation Done by Example.](https://raw.github.com/timothycrosley/examples/master/art/logo_large.png)](https://timothycrosley.github.io/examples/)\n_________________\n\n[![PyPI version](https://badge.fury.io/py/examples.svg)](http://badge.fury.io/py/examples)\n[![Build Status](https://travis-ci.org/timothycrosley/examples.svg?branch=master)](https://travis-ci.org/timothycrosley/examples)\n[![codecov](https://codecov.io/gh/timothycrosley/examples/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/examples)\n[![Join the chat at https://gitter.im/timothycrosley/examples](https://badges.gitter.im/timothycrosley/examples.svg)](https://gitter.im/timothycrosley/examples?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/examples/)\n[![Downloads](https://pepy.tech/badge/examples)](https://pepy.tech/project/examples)\n_________________\n\n[Read Latest Documentation](https://timothycrosley.github.io/examples/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/examples/)\n_________________\n\n**eXamples** (AKA: xamples for SEO) is a Python3 library enabling interactable, self-documenting, and self-verifying examples. These examples are attached directly to Python functions using decorators or via separate `MODULE_examples.py` source files.\n\n[![Example Usage Gif](https://raw.githubusercontent.com/timothycrosley/examples/master/art/example.gif)](https://raw.githubusercontent.com/timothycrosley/examples/master/art/example.gif)\n\nKey Features:\n\n* **Simple and Obvious API**: Add `@examples.example(*args, **kwargs)` decorators for each example you want to add to a function.\n* **Auto Documenting**: Examples, by default, get added to your functions docstring viewable both in interactive interpreters and when using [portray](https://timothycrosley.github.io/portray/) or [pdocs](https://timothycrosley.github.io/pdocs/).\n* **Signature Validating**: All examples can easily be checked to ensure they match the function signature (and type annotations!) with a single call (`examples.verify_all_signatures()`).\n* **Act as Tests**: Examples act as additional test cases, that can easily be verified using a single test case in your favorite test runner: (`examples.test_all_examples()`).\n* **Async Compatibility**: Examples can be attached and tested as easily against async functions as non-async ones.\n\nWhat's Missing:\n\n* **Class Support**: Currently examples can only be attached to individual functions. Class and method support is planned for a future release.\n\n## Quick Start\n\nThe following guides should get you up and running using eXamples in no time.\n\n1. [Installation](https://timothycrosley.github.io/examples/docs/quick_start/1.-installation/) - TL;DR: Run `pip3 install examples` within your projects virtual environment.\n2. [Adding Examples](https://timothycrosley.github.io/examples/docs/quick_start/2.-adding-examples/) -\n    TL;DR: Add example decorators that represent each of your examples:\n\n        # my_module_with_examples.py\n        from examples import example\n\n        @example(1, 1, _example_returns=2)\n        def add(number_1: int, number_2: int) -> int:\n            return number_1 + number_2\n\n3. [Verify and Test Examples](https://timothycrosley.github.io/portray/docs/quick_start/3.-testing-examples/) -\n    TL;DR: run `examples.verify_and_test_examples` within your projects test cases.\n\n        # test_my_module_with_examples.py\n        from examples import verify_and_test_examples\n\n        import my_module_with_examples\n\n\n        def test_examples_verifying_signature():\n            verify_and_test_examples(my_module_with_examples)\n\n4. Introspect Examples -\n\n        import examples\n\n        from my_module_with_examples import add\n\n\n        examples.get_examples(add)[0].use() == 2\n\n## Why Create Examples?\n\nI've always wanted a way to attach examples to functions in a way that would be re-useable for documentation, testing, and API proposes.\nJust like moving Python parameter types from comments into type annotations has made them more broadly useful, I hope examples can do the same for example calls.\n\nI hope you too find `eXamples` useful!\n\n~Timothy Crosley\n",
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

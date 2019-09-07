# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['final_class']

package_data = \
{'': ['*']}

install_requires = \
['typing_extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'final-class',
    'version': '0.2.0',
    'description': 'Final classes for Python 3',
    'long_description': "# final_class\n\n[![wemake.services](https://img.shields.io/badge/-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services) [![Build Status](https://travis-ci.org/moscow-python-beer/final-class.svg?branch=master)](https://travis-ci.org/moscow-python-beer/final-class) [![Coverage Status](https://coveralls.io/repos/github/moscow-python-beer/final-class/badge.svg?branch=master)](https://coveralls.io/github/moscow-python-beer/final-class?branch=master) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nFinal classes for `python3.6+`.\n\n\n## Features\n\n- No metaclass conflicts\n- No runtime overhead\n- No dependencies\n- Type hints included, [PEP-561](https://www.python.org/dev/peps/pep-0561/) and [PEP-591](https://www.python.org/dev/peps/pep-0591/) compatible\n- Designed to be as simple as possible\n\n\n## Why?\n\nIn languages like `java` we have a nice way\nto restrict subclassing any class by making it `final`:\n\n```java\npublic final class SomeClass {\n  // ...\n}\n```\n\nIn `python` we don't have such feature out of the box.\nThat's where `final_class` library comes in!\n\nThis package works perfectly with `@final` from `typing`.\nSo, with `final_class` you will have both type-checking and runtime checks.\n\n## Installation\n\n```bash\npip install final_class\n```\n\n\n## Usage\n\n```python\nfrom final_class import final\n\n\n@final\nclass Example(object):  # You won't be able to subclass it!\n    ...\n\n\nclass Error(Example):  # Raises `TypeError`\n    ...\n```\n\n## More?\n\nDo you want more? Check out:\n\n- [1-minute guide to real constants in Python](https://sobolevn.me/2018/07/real-python-contants)\n\n\n## License\n\nMIT.\n",
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/moscow-python-beer/final-class',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

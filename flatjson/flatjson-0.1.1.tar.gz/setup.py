# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flatjson']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'flatjson',
    'version': '0.1.1',
    'description': 'Flatten json.',
    'long_description': '## Flatjson\n\nFlatten JSON.\n\n## Installation\n\n`pip install flatjson`\n\n## Usage\n\n```python\nimport flatjson\n\ndata = {\n    "list":[{"a":1},{"b":True}],\n    "dict":{"c":1.1,"d":{"e":"string"}}\n}\nflatjson.dumps(data)\n\n# {\'list[0].a\': 1, \'list[1].b\': True, \'dict.c\': 1.1, \'dict.d.e\': \'string\'}\n```\n',
    'author': 'Jiuli Gao',
    'author_email': 'gaojiuli@gmail.com',
    'url': 'https://github.com/gaojiuli/flatjson',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

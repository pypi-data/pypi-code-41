# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['inari']

package_data = \
{'': ['*']}

extras_require = \
{'mkdocs': ['mkdocs']}

entry_points = \
{'console_scripts': ['inari = inari.cli:run'],
 'mkdocs.plugins': ['inari = inari.mkdocs_plugin:Plugin']}

setup_kwargs = {
    'name': 'inari',
    'version': '0.1.0',
    'description': 'Write docstrings in Markdown!',
    'long_description': '# inari\n\nWrite docstrings in Markdown!\n\n# Features\n\n* Minimum configuration.\n* No dependencies by default(but [MkDocs](https://www.mkdocs.org/) is recommended!).\n* CLI and MkDocs Plugin.\n* Cross reference in API documents.\n\n# Install\n\n```shell\npip install inari[mkdocs]\n```\n\n# Example\n\n```python\n# sample.py\n"""This is a sample module."""\n\nvariable = 42\n"""(`int`):  Docstrings for module-level variables."""\n\ndef func(foo: str, bar: int) -> str:\n    """\n    Docstrings for functions.\n\n    **Args**\n\n    * foo (`str`): First argument.\n    * bar (`int`): Second argument.\n\n    **Returns**\n\n    * `str`: Type of return value.\n\n    """\n    return foo * bar\n\nclass SampleClass:\n    """\n    Class docstrings.\n\n    **Attributes**\n\n    * baz (`str`): Docstrings for attributes.\n\n    """\n    baz: str\n\n    def __init__(self, b: str):\n        """\n        **Args**\n\n        * b (`str`): Arguments for initializing.\n\n        """\n\n        self.baz = b\n\n    def method(self, bar: int) -> str:\n        """\n        Method docstrings.\n\n        Cross reference available. `sample.func`\n\n        **Args**\n\n        * bar(`int`)\n\n        **Returns**\n\n        * `str`\n\n        """\n        return func(self.baz, bar)\n\n```\n\n```shell\ninari sample docs\n```\n\n`inari` makes this Markdown file:\n\n~~~markdown\n<!-- docs/sample-py.md -->\n# Module sample\n\nThis is a sample module.\n\n\n## Variables\n\n* **variable**{: #variable } (`int`):  Docstrings for module-level variables.\n\n## Classes\n\n### SampleClass {: #SampleClass }\n\n```python\nclass SampleClass(self, b: str)\n```\n\nClass docstrings.\n\n**Attributes**\n\n* **baz** (`str`): Docstrings for attributes.\n\n**Args**\n\n* **b** (`str`): Arguments for initializing.\n\n\n------\n\n#### Methods {: #SampleClass-methods }\n\n[**method**](#SampleClass.method){: #SampleClass.method }\n\n```python\ndef method(self, bar: int) -> str\n```\n\nMethod docstrings.\n\nCross reference available. [`func `](./#func)\n\n**Args**\n\n* **bar** (`int`)\n**Returns**\n\n* `str`\n\n## Functions\n\n### func {: #func }\n\n```python\ndef func(foo: str, bar: int) -> str\n```\n\nDocstrings for functions.\n\n**Args**\n\n* **foo** (`str`): First argument.\n* **bar** (`int`): Second argument.\n\n**Returns**\n\n* `str`: Type of return value.\n\n~~~\n\n# License\n\nMIT\n',
    'author': 'T.Kameyama',
    'author_email': 'tkamenoko@vivaldi.net',
    'url': 'https://tkamenoko.github.io/inari',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)

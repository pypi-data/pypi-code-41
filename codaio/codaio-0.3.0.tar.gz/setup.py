# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codaio']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'envparse>=0.2.0,<0.3.0',
 'inflection>=0.3.1,<0.4.0',
 'python-dateutil>=2.8,<3.0',
 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'codaio',
    'version': '0.3.0',
    'description': 'Python wrapper for Coda.io API',
    'long_description': "## Python wrapper for [Coda.io](https://coda.io) API\n\n[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)\n[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)\n\n\n### Installation\n```shell script\npip install codaio\n```\n\n### Config via environment variables\nThe following variables will be called from environment where applicable:\n\n* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)\n* `CODA_API_KEY` - your API key to use when initializing document from environment\n\n### Quickstart\nYou can initialize a document by providing API_KEY and document_id directly, or by storing your API key in environment under `CODA_API_KEY`\n\n```python\nfrom codaio import Document\n\n\n# Directly\ndoc = Document('YOUR_DOC_ID', 'YOUR_API_KEY')\n\n# From environment\n>>> doc = Document.from_environment('YOUR_DOC_ID')\n>>> print(doc)\nDocument(id='YOUR_DOC_ID', name='Document Name', owner='owner@example.com', browser_link='https://coda.io/d/URL')\n\n>>> doc.all_tables()\n[Table(name='Table1'), Table(name='table2')]\n\n>>> doc.get_table('Table1')\nTable(name='Table1')\n\n>>> table.columns\n[Column(name='First Column', calculated=False)]\n\n>>> table.rows\n[Row(name='Some row', index=1)]\n\n# Find row by column name and value:\n>> table.find_row_by_column_name_and_value('COLUMN_NAME', 'VALUE')\nRow(name='Some row', index=1)\n\n# Find row by column id and value\n>>> table.find_row_by_column_id_and_value('COLUMN_ID', 'VALUE')\nRow(name='Some row', index=1)\n\n# To get cell value for a column use getitem:\n>>> row['Column 1']\nCell(column=Column 1, row=Some row, value=Some Value)\n```\n\n#### Documentation\n\n`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)\n\n#### Using raw API\n\n`codaio` implements all methods of raw api in a convenient python manner. So API's `listDocs` becomes in `codaio` `Coda.list_docs()`. Get requests return a dictionary. Put, delete and post return a requests Response object.\n\nAll methods of Coda class are describe in the [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda).\n",
    'author': 'MB',
    'author_email': 'mb@blaster.ai',
    'url': 'https://github.com/Blasterai/codaio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

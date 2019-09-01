# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codaio']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'decorator>=4.4,<5.0',
 'envparse>=0.2.0,<0.3.0',
 'inflection>=0.3.1,<0.4.0',
 'python-dateutil>=2.8,<3.0',
 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'codaio',
    'version': '0.4.2',
    'description': 'Python wrapper for Coda.io API',
    'long_description': '## Python wrapper for [Coda.io](https://coda.io) API\n\n[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)\n![CircleCI](https://img.shields.io/circleci/build/github/Blasterai/codaio?label=CircleCI&token=843d9ce4140f18c098f242094684c32384c7bcc5)\n[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)\n![PyPI - Downloads](https://img.shields.io/pypi/dw/codaio)\n\n`codaio` is in active development stage. Issues and PRs very welcome!\n\n### Installation\n```shell script\npip install codaio\n```\n\n### Config via environment variables\nThe following variables will be called from environment where applicable:\n\n* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)\n* `CODA_API_KEY` - your API key to use when initializing document from environment\n\n### Quickstart using raw API\nCoda class provides a wrapper for all API methods. If API response included a JSON it will be returned as a dictionary from all methods. If it didn\'t a dictionary `{"status": response.status_code}` will be returned.\nIf request wasn\'t successful a `CodaError` will be raised with details of the API error.\n\n```python\nfrom codaio import Coda\n\ncoda = Coda(\'YOUR_API_KEY\')\n\n>>> coda.create_doc(\'My document\')\n{\'id\': \'NEW_DOC_ID\', \'type\': \'doc\', \'href\': \'https://coda.io/apis/v1beta1/docs/LINK\', \'browserLink\': \'https://coda.io/d/LINK\', \'name\': \'My Document\', \'owner\': \'your@email\', \'createdAt\': \'2019-08-29T11:36:45.120Z\', \'updatedAt\': \'2019-08-29T11:36:45.272Z\'}\n```\nFor full API reference for Coda class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda)\n\n### Quickstart using codaio objects\n\n`codaio` implements convenient classes to work with Coda documents: `Document`, `Table`, `Row`, `Column` and `Cell`.\n\n```python\nfrom codaio import Coda, Document\n\n# Initialize by providing a coda object directly\ncoda = Coda(\'YOUR_API_KEY\')\n\ndoc = Document(\'YOUR_DOC_ID\', coda=coda)\n\n# Or initialiaze from environment by storing your API key in environment variable `CODA_API_KEY`\ndoc = Document.from_environment(\'YOUR_DOC_ID\')\n\ndoc.list_tables()\n\ntable = doc.get_table(\'TABLE_ID\')\n\n# You can fetch a row by ID\nrow  = table[\'ROW_ID\']\n\n# Or fetch a cell by ROW_ID and COLUMN_ID\ncell = table[\'ROW_ID\'][\'COLUMN_ID\']  \n\n# This is equivalent to getting item from a row\ncell = row[\'COLUMN_ID\']\n\n# Get a column to find it\'s id\ncolumn = table.get_column_by_name(\'COLUMN_NAME\')\ncell = row[column.id]\n\n# To set a cell value \ncell.value = \'foo\'\n\n# Please mind that this takes a while in the current API, so you\'ll need to manually check when the value returns correct\n# You can manually refresh row cells by calling:\nrow.refresh()\n\n\n# Iterate over rows -> delete rows that match a condition\nfor row in table.rows():\n    if row[\'COLUMN_ID\'] == \'foo\':\n        row.delete()\n\n# Iterate over rows -> edit cells in rows that match a condition\nfor row in table.rows():\n    if row[\'COLUMN_ID\'] == \'bar\':\n        row[\'COLUMN_ID\'] = \'spam\'\n```\n\nFor full API reference for Document class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Document)\n\n#### Documentation\n\n`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)\n\n\n#### Testing\n\nAll tests are in the `/tests` folder. It\'s a little bit problematic to test against the live API since some responses may take a bit longer, so test results are not reliable enough to use a CI system.\n\nCheck out the fixtures if you want to improve the testing process.\n',
    'author': 'MB',
    'author_email': 'mb@blaster.ai',
    'url': 'https://github.com/Blasterai/codaio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

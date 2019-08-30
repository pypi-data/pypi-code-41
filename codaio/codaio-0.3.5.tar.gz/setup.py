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
    'version': '0.3.5',
    'description': 'Python wrapper for Coda.io API',
    'long_description': '## Python wrapper for [Coda.io](https://coda.io) API\n\n[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)\n[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)\n\n\n### Installation\n```shell script\npip install codaio\n```\n\n### Config via environment variables\nThe following variables will be called from environment where applicable:\n\n* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)\n* `CODA_API_KEY` - your API key to use when initializing document from environment\n\n### Quickstart using raw API\nCoda class provides a wrapper for all API methods. If API response included a JSON it will be returned as a dictionary from all methods. If it didn\'t a dictionary `{"status": response.status_code}` will be returned.\nIf request wasn\'t successful a `CodaError` will be raised with details of the API error.\n\n```python\nfrom codaio import Coda\n\ncoda = Coda(\'YOUR_API_KEY\')\n\n>>> coda.create_doc(\'My document\')\n{\'id\': \'NEW_DOC_ID\', \'type\': \'doc\', \'href\': \'https://coda.io/apis/v1beta1/docs/LINK\', \'browserLink\': \'https://coda.io/d/LINK\', \'name\': \'My Document\', \'owner\': \'your@email\', \'createdAt\': \'2019-08-29T11:36:45.120Z\', \'updatedAt\': \'2019-08-29T11:36:45.272Z\'}\n```\nFor full API reference for Coda class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda)\n\n### Quickstart using codaio objects\n\n`codaio` implements convenient classes to work with Coda documents: `Document`, `Table`, `Row`, `Column` and `Cell`.\n\n```python\nfrom codaio import Coda, Document, Table\n\n# Initialize by providing a coda object directly\ncoda = Coda(\'YOUR_API_KEY\')\n\ndoc = Document(\'YOUR_DOC_ID\', coda=coda)\n\n# Or initialiaze from environment by storing your API key in environment variable `CODA_API_KEY`\ndoc = Document.from_environment(\'YOUR_DOC_ID\')\n\ndoc.list_tables()\n\ntable: Table = doc.get_table(\'TABLE_ID\')\n```\n\nFor full API reference for Document class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Document)\n\n#### Documentation\n\n`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)\n',
    'author': 'MB',
    'author_email': 'mb@blaster.ai',
    'url': 'https://github.com/Blasterai/codaio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

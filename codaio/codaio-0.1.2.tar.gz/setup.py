# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codaio']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'python-dateutil>=2.8,<3.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'codaio',
    'version': '0.1.2',
    'description': 'Python wrapper for Coda.io API',
    'long_description': "## Python wrapper for [Coda.io](https://coda.io) API\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n### Installation\n```shell script\npip install codaio\n```\n\n### Config via environment variables\nThe following variables will be called from environment where applicable:\n\n* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)\n* `CODA_API_KEY` - your API key to use when initializing document from environment\n\n### Usage\nYou can initialize a document by providing API_KEY and document_id directly, or by storing yoru API key in environment under `CODA_API_KEY`\n\n```python\nfrom codaio import Document\n\n# Directly\ndoc = Document('YOUR_DOC_ID', 'YOUR_API_KEY')\n\n# From environment\ndoc = Document.from_environment('YOUR_DOC_ID')\n\nprint(doc)\n>>> Document(id='YOUR_DOC_ID', name='Document Name', owner='owner@example.com', browser_link='https://coda.io/d/URL')\n```\n\n#### Methods\n\n```python\nfrom codaio import Document\n\ndoc = Document.from_environment('YOUR_DOC_ID')\n\ndoc.tables() # list all tables\ndoc.get_table_rows(table_id_or_name='YOUR_TABLE')  # get ALL table rows\ndoc.get_table_rows(table_id_or_name='YOUR_TABLE', query={'query'})\n```\n\n#### Using raw API\n\nYou can issue [raw API requests](https://coda.io/developers/apis/v1beta1#tag/Docs) directly using Document methods `get` and `post`. You can skip entire url up to `/docs/{docId}`, this is handled by the wrapper. So for request to `https://coda.io/apis/v1beta1/docs/{docId}/tables` just use endpoint value of `/tables`:\n\n```python\nfrom codaio import Document\n\ndoc = Document.from_environment('YOUR_DOC_ID')\n\ntables = doc.get(endpoint='/tables')\n```\n\nYou can also use `offset` and `limit` to get a portion of results. If limit is not set, all the data will be automatically fetched. Pagination is handled for you by the wrapper.\n\n### Contributing\nAll contributions, issues and PRs very welcome!\n",
    'author': 'MB',
    'author_email': 'mb@blaster.ai',
    'url': 'https://github.com/Blasterai/codaio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

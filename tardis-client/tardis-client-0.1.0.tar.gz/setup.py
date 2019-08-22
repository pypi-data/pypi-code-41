# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tardis_client']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.4.0,<0.5.0', 'aiohttp>=3.5,<4.0']

setup_kwargs = {
    'name': 'tardis-client',
    'version': '0.1.0',
    'description': 'Python client for tardis.dev - historical tick-level cryptocurrency market data replay API.',
    'long_description': '# tardis-client\n\nPython client for tardis.dev - historical tick-level cryptocurrency market data replay API.\n\n## Usage\n\n```python\nimport asyncio\nfrom tardis_client import TardisClient, Channel\n\n\nasync def replay():\n    tardis_client = TardisClient()\n\n    messages = tardis_client.replay(\n        exchange="bitmex",\n        from_date="2019-06-01",\n        to_date="2019-06-02",\n        filters=[Channel(name="trade", symbols=["XBTUSD","ETHUSD"]), Channel("orderBookL2", ["XBTUSD"])],\n    )\n\n    async for local_timestamp, message in messages:\n        print(message)\n\n\nasyncio.run(replay())\n```\n',
    'author': 'Thad',
    'author_email': 'thad@tardis.dev',
    'url': 'https://github.com/tardis-dev/python-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)

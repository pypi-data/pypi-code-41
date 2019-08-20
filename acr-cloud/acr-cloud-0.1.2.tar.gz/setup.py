# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['acr_cloud']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'acr-cloud',
    'version': '0.1.2',
    'description': 'acrcloud music recognition wrapper',
    'long_description': "# ACR-Cloud\n[![image](https://img.shields.io/pypi/v/acr-cloud.svg)](https://pypi.org/project/acr-cloud/)\n[![image](https://img.shields.io/pypi/l/acr-cloud.svg)](https://pypi.org/project/acr-cloud/)\n[![image](https://img.shields.io/pypi/pyversions/acr-cloud.svg)](https://pypi.org/project/acr-cloud/)\n\nAn ACR-Cloud API Python client library\n\n## Installation\nfrom PyPI\n```\n$ pip install acr-cloud\n```\n\nfrom git repository\n```\n$ pip install git+https://github.com/Live-Lyrics/acrcloud-py\n```\n\nfrom source\n```\n$ git clone https://github.com/Live-Lyrics/acrcloud-py\n$ cd acrcloud-py\n$ python setup.py install\n```\n\n## Version upgrade\n```\n➜ pip install --upgrade acr-cloud\n```\n\n### Requirements\n* Python 3.5 and up\n\n## Usage\n\nBefore you can begin identifying audio with ACRCloud's API, you need to sign up for a free trial over at \nhttps://www.acrcloud.com and create an Audio & Video recognition project. \nThis will generate a `host`, `access_key`, and `access_secret` for you to use.\n\n```python\nfrom acr_cloud import ACRCloud\n\nacr = ACRCloud('eu-west-1.api.acrcloud.com', 'access_key', 'access_secret')\nmetadata = acr.identify('path-to-file.ogg')\nprint(metadata)\n```\n\n## Development setup\nUsing [Poetry](https://poetry.eustace.io/docs/)   \n```\n$ poetry install\n```\nor [Pipenv](https://docs.pipenv.org/)   \n```\n$ pipenv install --dev -e .\n```\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)",
    'author': 'Andriy Orehov',
    'author_email': 'andriyorehov@gmail.com',
    'url': 'https://github.com/andriyor/acrcloud-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

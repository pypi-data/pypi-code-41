# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['amalgama']

package_data = \
{'': ['*']}

install_requires = \
['pyquery>=1.4,<2.0', 'python-slugify>=2.0,<3.0', 'unidecode>=1.0,<2.0']

setup_kwargs = {
    'name': 'amalgama',
    'version': '0.2.2',
    'description': 'amalgama scraper',
    'long_description': "# Amalgama-pq \n[![image](https://img.shields.io/pypi/v/amalgama.svg)](https://pypi.org/project/amalgama/)\n[![image](https://img.shields.io/pypi/l/amalgama.svg)](https://pypi.org/project/amalgama/)\n[![image](https://img.shields.io/pypi/pyversions/amalgama.svg)](https://pypi.org/project/amalgama/)\n[![Build Status](https://travis-ci.org/Live-Lyrics/amalgama-pq.svg?branch=master)](https://travis-ci.org/Live-Lyrics/amalgama-pq)\n[![codecov](https://codecov.io/gh/Live-Lyrics/amalgama-pq/branch/master/graph/badge.svg)](https://codecov.io/gh/Live-Lyrics/amalgama-pq)\n\nAmalgama lyrics scraping\n\n### Requirements\n* Python 3.5 and up\n\n## Installation\nfrom PyPI\n```\n$ pip install amalgama\n```\n\nfrom git repository\n```\n$ pip install git+https://github.com/andriyor/amalgama-pq.git#egg=amalgama-pq\n```\n\nfrom source\n```\n$ git clone https://github.com/andriyor/amalgama-pq.git\n$ cd amalgama-pq\n$ python setup.py install\n```\n\n## Usage\n\n```python\nimport requests\n\nimport amalgama\n\nartist, song = 'Pink Floyd', 'Time'\nurl = amalgama.get_url(artist, song)\ntry:\n    response = requests.get(url)\n    response.raise_for_status()\n    text = amalgama.get_first_translate_text(response.text)\n    print(f'{text}{url}')\nexcept requests.exceptions.HTTPError:\n    print(f'{artist}-{song} not found in amalgama {url}')\n```\n\nExpected output \n```\nTime (оригинал Pink Floyd)\n\nTicking away the moments that make up a dull day\nYou fritter and waste the hours in an off hand way\nKicking around on a piece of ground in your home town\nWaiting for someone or something to show you the way\n...\n\nВремя (перевод Дмитрий Попов из Новокузнецка)\n\nТикают секунды, наполняя скучный день,\nТы разбрасываешься по мелочам и понапрасну тратишь время,\nВертишься вокруг клочка земли родного города,\nВ ожидании, что кто-то или что-то укажет тебе путь.\n...\n```\n\n## Development setup\nUsing [Poetry](https://poetry.eustace.io/docs/)   \n```\n$ poetry install\n```\nrun tests\n```\n$ poetry run pytest\n```\nor [Pipenv](https://docs.pipenv.org/)   \n```\n$ pipenv install --dev -e .\n```\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)",
    'author': 'Andriy Orehov',
    'author_email': 'andriyorehov@gmail.com',
    'url': 'https://github.com/andriyor/amalgama-pq',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

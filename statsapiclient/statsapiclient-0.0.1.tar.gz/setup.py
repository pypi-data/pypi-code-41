# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['statsapiclient', 'statsapiclient.games']

package_data = \
{'': ['*']}

install_requires = \
['jupyter>=1.0,<2.0', 'jupyterthemes>=0.20.0,<0.21.0', 'requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'statsapiclient',
    'version': '0.0.1',
    'description': '',
    'long_description': "statsapiclient: A client for the NHL stats API\n==============================================\n\nPurpose\n-------\n\nTo provide a Python client to access the NHL's JSON API including game, play, and player data.\n\nInstallation\n------------\n\nTBD\n\nModule Specs\n------------\n\nSchedule\n^^^^^^^^\n\ngames_from_date\n\ngames_from_date_range\n\n\nGames\n^^^^^\n\ngame_line_score\n\ngame_play_by_play (TBD)\n\ngame_box_score (TBD)\n\n\nTeams\n^^^^^\n\nteams_all\n\nteams_by_conference\n\nteams_by_division\n\n\nPlayers\n^^^^^^^\n\nTBD\n\n\nExamples\n^^^^^^^^\n\nTBD\n",
    'author': 'Brett LaBombarda',
    'author_email': 'bplabombarda@gmail.com',
    'url': 'https://github.com/hockeymonkeys/statsapiclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

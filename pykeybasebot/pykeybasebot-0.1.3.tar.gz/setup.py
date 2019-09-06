# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pykeybasebot',
 'pykeybasebot.types',
 'pykeybasebot.types.chat1',
 'pykeybasebot.types.gregor1',
 'pykeybasebot.types.keybase1',
 'pykeybasebot.types.stellar1']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.3.2,<0.4.0']

setup_kwargs = {
    'name': 'pykeybasebot',
    'version': '0.1.3',
    'description': 'Officially supported Keybase python bot client library',
    'long_description': "# pykeybasebot\n\nThis is the officially support Keybase Python library. It is an unopinionated, simple wrapper around the Keybase CLI API for creating an interactive bot or general scripting. This library does not attempt to do intent parsing or manage state at all. You'll have to build that yourself, but with the examples, this library will hopefully make whatever you want to build much much easier `:)`.\n\nThere are also similar libraries for [JavaScript](https://github.com/keybase/keybase-bot) and [Go](https://github.com/keybase/pykeybasebot).\n\nThis library is very far from exhaustively covering the complete Keybase API, but it is our hope that it will be easy to add to (see chat_client.py for the pattern). It currently does reading from channels and writing messages/reactions pretty well. That's enough for the vast majority of basic functionality. Future work can add teams behavior, more wallet functionality (e.g. sending money), ...\n\n## Installation\n\n```\npip install pykeybasebot\n```\n\nPython 3.7 or greater, please. And it's all async, so you'll need to call into it with that in mind.\n\n## Setup\n\nGenerally speaking, here's what you need to do:\n\n1. Create a handler function that takes event objects and does something with them. This function will get called with your bot instance (described below) and the KbEvent instance.\n2. Create a bot. You _must_ initialize this with the handler function to call with each event. You _may_ optionally pass in: (1) the username and/or paperkey for the bot's identity (it'll default to the currently logged-in user otherwise), (1) the event loop that you want new tasks to be sent to (this is necessary if you want to lock on async behavior -- see the examples), (2) the location of the running keybase app (defaults to `keybase` which is fine if it's in your PATH), your user's home directory, or pid_file. These three are more useful for complicated local development with multiple accounts and less useful if you're running in a docker container or as the only user on your system.\n3. If you are not already running on a logged-in device, you need to do that. We recommend doing this with the `oneshot` command. It's in the examples.\n4. start the bot inside the asyncio event loop. This bot command wraps `keybase chat api-listen`, (and it takes basically the same exact options) and fires off events to your handler function.\n\n## Examples\n\nDefinitely definitely check out the examples. We're really counting on them to make it clear how to use this library.\n\n## Contributing\n\nPRs are extremely welcome. To start:\n\n```\ngit clone https://github.com/keybase/pykeybasebot\ncd pykeybasebot\n```\n\nWe use [Poetry](https://poetry.eustace.io/) to handle our packaging. Go check out their website for installation instructions. To start Poetry, you'll need the `python` executable in your path to link to Python 3.7. We recommend using [pyenv](https://github.com/pyenv/pyenv) to handle different versions of Python on your machine. With pyenv installed, it should automatically set `python` to 3.7 when you `cd` into this repo.\n\nOnce you have the right Python version, you can run:\n\n```\npip install poetry\npoetry install\n```\n\nThis will set up a virtualenv for you and install all the dependencies needed into it!\n\n### Static code analysis tools\n\nWe use a few different static analysis tools to perform linting, type-checking, formatting, etc. The correct versions should be install when you run `poetry install`, but you'll probably want to configure your editor to work with:\n\n- [mypy](http://www.mypy-lang.org/) (Type checking)\n- [black](https://github.com/psf/black) (code formatting)\n- [isort](https://github.com/timothycrosley/isort) (import formatting)\n- [flake8](http://flake8.pycqa.org) (linting)\n\n#### pre-commit hooks\n\nWe check all git commits with the above tools with\n[pre-commit.com](http://pre-commit.com) pre-commit hooks.\nTo enable use of these pre-commit hooks:\n\n- [Install](http://pre-commit.com/#install) the `pre-commit` utility.\n- Remove any existing pre-commit hooks via `rm .git/hooks/pre-commit`\n- Configure via `pre-commit install`\n\nThen proceed as normal.\n\n### Testing\n\nTo run tests, type\n\n```\npoetry run python -m pytest\n```\n\nTests are admittedly weak. You could change that!\n\n### Types\n\nMost of the types the bot uses are generated from definitions defined in the [`protocol/`](https://github.com/keybase/client/tree/master/protocol) directory inside the Keybase client repo. This ensures that the types that the bot uses are consistent across bots and always up to date with the output of the API.\n\nTo build the types for the Python bot, you'll need to clone the `client` repo. This requires [Go](https://golang.org/) and your [GOPATH](https://github.com/golang/go/wiki/SettingGOPATH) to be set up.\n\n```shell\ngo get github.com/keybase/client/go/keybase\n```\n\nand install the necessary dependencies for compiling the protocol files. This requires [node.js](https://nodejs.org) and [Yarn](https://yarnpkg.com).\n\n```shell\ncd client/protocol\nyarn install\n```\n\nThen you can generate the types by using the provided Makefile in this repo.\n\n```shell\ncd path/to/keybase-bot\nmake\n```\n\nShould you need to remove all the types for some reason, you can run `make clean`.\n\n### Publishing\n\nPoetry can build and publish packages to PyPI. We've run into some issues with uploading to PyPI and Poetry, though, so for now we're recommending building with Poetry and uploading with Twine.\n\n```shell\npoetry build\n# Upload to Test PyPi. You only need to run the first command once\npoetry config repositories.testpypi https://test.pypi.org/legacy/\npoetry publish -r testpypi\n# Upload to real PyPi\npoetry publish\n```\n",
    'author': 'Keybase Engineering Team',
    'author_email': 'alex@keyba.se',
    'url': 'https://github.com/keybase/pykeybasebot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

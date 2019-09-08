# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['quare']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0',
 'colorama>=0.4.1,<0.5.0',
 'dateparser>=0.7.1,<0.8.0',
 'keyring>=18.0,<19.0',
 'terminaltables>=3.1,<4.0',
 'websocket-client>=0.56.0,<0.57.0']

entry_points = \
{'console_scripts': ['quare = quare.cli:main']}

setup_kwargs = {
    'name': 'quare',
    'version': '0.2.3',
    'description': 'quare is a CLI client for Quip.',
    'long_description': '# quare\n\n[![pipeline status](https://gitlab.com/jstvz/quare/badges/master/pipeline.svg)](https://gitlab.com/jstvz/quare/commits/master)\n[![coverage report](https://gitlab.com/jstvz/quare/badges/master/coverage.svg)](https://gitlab.com/jstvz/quare/commits/master)\n[![PyPI - License](https://img.shields.io/pypi/l/quare.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)\n![PyPI](https://img.shields.io/pypi/v/quare.svg)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quare.svg)\n![PyPI - Status](https://img.shields.io/pypi/status/quare.svg)\n\nInteract with Quip from the command line.\n\n![quare streaming messages](https://github.com/jstvz/quare/blob/master/docs/assets/quare.png?raw=true)\n\n## Introduction ##\nquare allows interaction with [Quip](https://quip.com) via the command line. While `quare` is in alpha, there are some features you may find useful:\n- Pipe the output of a command to a chat or document and format it as monospace.\n- Archive messages by piping them into a local file\n- Securely store authentication tokens for multiple Quip instances.\n\nThis tool is in its early stages of development, and is subject to change (or abandonment) at any time. Use at your own risk.\n\n## Installation ##\n\n```console\n$ pipx install quare\n```\n\n## Usage ##\n\n### Authentication ###\nStore a Quip API token (See: https://quip.com/dev/token):\n\n```console\n$ quare auth\nToken: long_token_string\nToken stored.\n```\nIf you have multiple Quip instances (like multiple Slack Workspaces), you can specify an alias for them. You can also pass your token directly to `auth`:\n\n```console\n$ quare msg auth --alias test_server --token \'t1DJBQWBXHCYgh1=|2983928392|nYtRFIhV7nl4...\'\n```\n\n#### Whoami ####\n\nTo see information about the logged in user:\n```console\n$ quare msg whoami\n┌Default───────┬───────────────┐\n│ Name         │ Tests Testeri │\n├──────────────┼───────────────┤\n│ Email(s)     │ t@testz.dev   │\n├──────────────┼───────────────┤\n│ Quip User ID │ mRLA6Zdn3PO   │\n└──────────────┴───────────────┘\n```\n\n### Sending messages ###\nThe destination may be a document or chat:\n\n```console\n$ quare msg send --room room_id --content \'Hello everyone!\'\n```\n\n#### Pipe content from `stdin` ####\n\nMessage content can be piped from `stdin`:\n```console\n$ uname -a | quare msg send --room room_id --content \'-\'\n```\n\nWhile Quip allows formatting messages using some markdown markup, it doesn\'t recognize markdown code blocks ("\\`\\`\\`"). To define a code block, use the `--monospace` option:\n\n```console\n$ dmesg | tail -n 5 | quare msg send --room room_id --content \'-\' --monospace\n```\n\n### Receiving messages ###\n\n#### Stream to stdout ####\nTo stream every message appearing in the Updates tab:\n\n```console\n$ quare msg stream\nStreaming updates... press Ctrl-C to exit.\n[Sun Jun 30 17:23:09 2019 | (Test Log) | @Tests Testeri] ok ok\n```\n\n#### Dump the content of a chat room ####\nTo get the last 5 messages in a chat room or document:\n```console\n$ quare msg get --room room_id --last 5\n[Sat Jun 29 03:19:09 2019 | @Tester Testeri] This is a monologue!\n[Sat Jun 29 16:00:12 2019 | @Tester Testeri] ok\n[Sat Jun 29 16:34:51 2019 | @Tester Testeri] I\'m done!\n[Sun Jun 30 17:30:14 2019 | @Tester Testeri] 🌮\n[Sun Jun 30 17:30:27 2019 | @Tester Testeri] 🥃\n```\n\nTo get the last 2 messages as JSON:\n```console\n$ quare msg get  -r "IcTAAAtVxXb" --last 2 --json\n[{"author_id": "mRLA6Zdn3PO", "visible": true, "id": "IcderpEe8wG", "created_usec": 1561849212672040, "updated_usec": 1561849212696571, "text": "ok", "author_name": "Tester Testeri"}, {"author_id": "mRLA6Zdn3PO", "visible": true, "id": "IcNodg7n2Tx", "created_usec": 1561851291612434, "updated_usec": 1561851291620308, "text": "chat", "author_name": "Tester Testeri"}]\n```\n\nTo dump the last 200 messages in a chat room into a text file:\n```console\n$ quare msg get --room room_id --last 200 > interesting_conversation.log\n```\n\nTo get all messages since a datetime:\n```console\n$ quare msg get --room room_id --since 2019-01-01T00:32:00Z > greppable_archive.log\n```\n\nThe `--since` option recognizes any date recognized by [dateparser](https://dateparser.readthedocs.io/en/latest/):\n```console\n$ quare msg get --room room_id --since \'Monday\' > this_week.log\n$ quare msg get --room room_id --since \'2 months ago\' > this_quarter.log\n```\n\n### Editing documents ###\n\nTo append a markdown file to an existing document\n```console\n$ quare doc append --id xxxDoc_IDxxx --file /tmp/foo.md\n$ cat /tmp/foo.md | quare doc append --id xxxDoc_IDxxx --file -\n```\n\nTo append a markdown-format string to an existing document\n```console\n$ quare doc append --id xxxDoc_IDxxx --content \'## Headline\\n\\n\'\n```\n\n## Development ##\n\nThis work is licensed under the terms of the [LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html).\n### Contributions ###\nSee CONTRIBUTING.rst\n',
    'author': 'James Estevez',
    'author_email': 'j@jstvz.org',
    'url': 'https://github.com/jstvz/quare',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

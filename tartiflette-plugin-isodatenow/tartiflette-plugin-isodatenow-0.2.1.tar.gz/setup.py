# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tartiflette_plugin_isodatenow']

package_data = \
{'': ['*']}

install_requires = \
['tartiflette>=0.12.5,<0.13.0']

setup_kwargs = {
    'name': 'tartiflette-plugin-isodatenow',
    'version': '0.2.1',
    'description': 'ISO Date Formatter for Tartiflette',
    'long_description': '# tartiflette-plugin-isodatenow\n\n<a href="https://buddy.works"><img src="https://assets.buddy.works/automated-dark.svg" alt="Buddy.Works logo."></img></a>\n\n[![buddy pipeline](https://app.buddy.works/benriggleman/tartiflette-plugin-isodate/pipelines/pipeline/208276/badge.svg?token=ff05a3fb6bb08b48350b4170e0c447aa3ccc198abbddd48c222205c3c61a7cff "buddy pipeline")](https://app.buddy.works/benriggleman/tartiflette-plugin-isodate/pipelines/pipeline/208276)\n\nISO Date Format Directive for Tartiflette\n\n## TOC\n- [Overview](#overview)\n- [Installation](#install)\n- [Usage](#usage)\n    - [Options](#usage-options)\n        - [microseconds](#usage-options-microseconds)\n        - [timezone](#usage-options-timezone)\n        - [utc](#usage-options-utc)\n\n\n## [Overview](#overview)\n\nThe `tartiflette-plugin-isodatenow` plugin adds an `@isoDateNow` directive to [tartiflette](https://github.com/tartiflette/tartiflette).  It sets the field that it is on with the current time in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601).\nIt is primarly intended for use in mutations as the directive overrides any value sent though it can be used in queries where a `createdAt` or response timestamp is required.\n\n## [Installation](#install)\n\nTo install with [poetry](https://poetry.eustace.io):\n\n```sh\n$ poetry add tartiflette-plugin-isodatenow\n```\n\nTo install with pip:\n\n```sh\n$ pip install tartiflette-plugin-isodatenow\n```\n\n## [Usage](#usage)\n\n```graphql\ntype Example {\n    createdAt: String @isoDateNow\n}\n```\n\nQuerying `createdAt` would return the following:\n\n```json\n{\n    "data": {\n        "example": {\n            "createdAt": "2019-09-04T13:49:12.585158+00:00"\n        }\n    }\n}\n```\n\n\n### [Options](#usage-options)\n\nThe `@isoDateNow` also takes the following optional arguments:\n\n#### [@isoDateNow(microseconds: false)](#usage-options-microseconds)\n\nReturns date and time _without_ microseconds.\n\n```graphql\ntype Example {\n    createdAt: String @isoDateNow(microseconds: false)\n}\n```\n\nQuerying `createdAt` would return the following:\n\n```json\n{\n    "data": {\n        "example": {\n            "createdAt": "2019-09-04T13:49:12+00:00"\n        }\n    }\n}\n```\n\n#### [@isoDateNow(timezone: false)](#usage-options-timezone)\n\nReturns date and time _without_ timezone.\n\n```graphql\ntype Example {\n    createdAt: String @isoDateNow(timezone: false)\n}\n```\n\nQuerying `createdAt` would return the following:\n\n```json\n{\n    "data": {\n        "example": {\n            "createdAt": "2019-09-04T13:49:12.585158"\n        }\n    }\n}\n```\n\n#### [@isoDateNow(utc: false)](#usage-options-utc)\n\nReturns date and time in the _local_ timezone.\n\n```graphql\ntype Example {\n    createdAt: String @isoDateNow(utc: false)\n}\n```\n\nQuerying `createdAt` would return the following:\n\n```json\n{\n    "data": {\n        "example": {\n            "createdAt": "2019-09-04T09:49:12.585158-04:00"\n        }\n    }\n}\n```\n\n\nThe arguments can be used in any combination and will return an [ISO8601 compliant date](https://en.wikipedia.org/wiki/ISO_8601).\n\nFor example settings `microseconds` to `false` and `timezone` to `true` would yield: 2019-09-04T13:49:12+00:00.\n\nPossible combinations:\n\n- `@isoDateNow` >> "2019-09-04T13:49:12.585158+00:00"\n- `@isoDateNow(timezone: false)` >> "2019-09-04T13:52:43.476260"\n- `@isoDateNow(microseconds: false)` >> "2019-09-04T13:50:02+00:00"\n- `@isoDateNow(microseconds: false, timezone: false)` >> "2019-09-04T13:53:31"\n\nThe time can also be set to the `local` time by setting `utc` to `false`.  \n\n`@isoDateNow(utc: false)` >> "2019-09-04T09:50:02+00:00"\n\nUsing the `@isoDateNow` directive will override any value sent.',
    'author': 'Ben Riggleman',
    'author_email': 'ben.riggleman@gmail.com',
    'url': 'https://github.com/briggleman/tartiflette-plugin-isodate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flask_socketio_lit_html']

package_data = \
{'': ['*'], 'flask_socketio_lit_html': ['webcomponent_templates/*']}

setup_kwargs = {
    'name': 'flask-socketio-lit-html',
    'version': '0.1.0rc5',
    'description': 'Simple Webcomponents with flask',
    'long_description': '[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-flask-4ab?style=for-the-badge&labelColor=4cd)](https://palletsprojects.com/p/flask/)\n[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-lit%20html-4ab?style=for-the-badge&labelColor=4cd)](https://lit-html.polymer-project.org/)\n[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-Socket.IO-4ab?style=for-the-badge&labelColor=4cd)](https://socket.io/)\n\n![Version: Alpha](https://img.shields.io/badge/version-alpha-yellow?style=for-the-badge)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)\n[![Pypi version](https://img.shields.io/pypi/v/flask-socketio-lit-html?style=for-the-badge)](.)\n[![ReadTheDocs](https://readthedocs.org/projects/flask-socketio-lit-html/badge/?version=latest&style=for-the-badge)](https://flask-socketio-lit-html.readthedocs.io/)\n![Travis (.org)](https://img.shields.io/travis/playerla/flask-socketio-lit-html?style=for-the-badge)\n\n# Flask-Socket.IO-lit-html\n\nWebcomponents with Flask and SocketIO\n\n## Proof of concept project to use Webcomponents in Python Flask\n\n* Generate a restful API (inspired from Flask-Restful)\n* Update html on data changes through socketio (Inspired from Angular properties reflection)\n\n## Usage philosophy\n\nCreate user webcomponent from sqlalchemy design:\n```python\nclass User(db.Model):\n    username = db.Column(db.String(80), nullable=False)\n\nblueprint = User.register("/user", "user-item", "user.html")\napp.register_blueprint(blueprint)\n```\nDisplay the second user of your database:\n```html\n<script type="module" src="{{url_for(\'user-item.webcomponent\')}}"></script>\n<div> user 2: <user-item index=2 ></user-item></div>\n```\n\nThis code represent the idea behind the module, it\'s not real code, look at app.py for a working example.\n\n## Contribute : Pull requests are welcome !\n\n[![Edit with Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/playerla/flask-socketio-lit-html/tree/Dev)\n\n### Updating autodoc\n\n```sh\ncd docs && sphinx-apidoc -o source/ ../flask_socketio_lit_html\n```\n\n### Build and publish package\n\n```sh\npoetry build\n```\nJust increment the version in [pyproject.toml](./pyproject.toml) to publish after tests are succesfully passed (see [.travis.yml](./.travis.yml))\n',
    'author': 'playerla',
    'author_email': 'playerla.94@gmail.com',
    'url': 'https://github.com/playerla/flask-socketio-lit-html',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

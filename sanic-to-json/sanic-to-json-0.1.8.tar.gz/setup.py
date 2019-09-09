# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sanic_to_json']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sanic-to-json',
    'version': '0.1.8',
    'description': 'Create Postman JSON API documentation files from Sanic.',
    'long_description': '<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n\n[![Build Status](https://travis-ci.org/kountable/sanic-to-json.svg?branch=master)](https://travis-ci.org/kountable/sanic-to-json)\n\n# sanic-to-json\nGenerate a Postman [JSON](http://json.org) file from a [Sanic app](https://sanic.readthedocs.io/en/latest/index.html#). The JSON file can directly uploaded into the [Postman client](https://www.getpostman.com) or through their [API](https://docs.api.getpostman.com/?version=latest#3190c896-4216-a0a3-aa38-a041d0c2eb72).  \n\nUsing the postman [schema](https://schema.getpostman.com/json/collection/v2.1.0/collection.json) we can build Postman Collections using python endpoints from Sanic (Flask apps need testing). The script parses the Sanic app. It searches for blueprints. The blueprints, through routes, provide docs strings data. The doc string data is used to populate a Postman formatted JSON file. The JSON file can then be uploaded to Postman as a collection. \n\nOnce we have Postman formatted JSON we can create API documentation through the Postman [API](https://docs.api.getpostman.com/?version=latest#3190c896-4216-a0a3-aa38-a041d0c2eb72)\n\n## How to use\n\n- to execute an example run `python -m examples.example_script`\nwhich executes\n```python\nfrom sanic_to_json import generate_sanic_json\nfrom examples.app import app\n\ngenerate_sanic_json("Test API", app, filename="postman_collection.json")\n```\nThe above code formats the Postman collection with \'Test API\' and doc strings from Sanic app, `app`, and yields [postman_collection.json](https://github.com/kountable/sanic-to-json/blob/master/postman_collection.json)\n\n### To add `body` and `header` elements to Postman JSON \nPlacing `INI` in doc string will cause the text below to be loaded into a python config object, which then get converted to the appropiate headers and JSON body in Posttman. \n\nFor example, as found in [endpoint-three](https://github.com/kountable/sanic-to-json/blob/master/examples/blueprint_1.py)\n```\n    INI\n    [request]\n    header = {"Content-Type": "application/json"}\n    body = {"username": "{{username}}", "password": "{{password}}"}\n```\n\n### To add query parameters\nSimilar to above placing sections under INI that are prefixed will start a example request. \nFor example, as found in [endpoint-one](https://github.com/kountable/sanic-to-json/blob/master/examples/blueprint_1.py)\n```\n    """Return text from request.\n       \n    INI\n    [request]\n    header = {"Content-Type": "application/json","x-amz-sns-message-type": "Notification"}\n    query = ?day=1&temp=F\n    """\n```\n\n## How to document Sanic app and Blueprints\n- As the example shows, the Sanic app should have a `.doc` attribute. This doc string will serve as the introduction to the API in Postman docs, e.g., `app.__doc__ = "This API does stuff."`\n\n- Blueprints should also include a doc string, this will serve as the description to each collection folder in Postman. Again see `examples` folder\n`bp1.__doc__ = "This is the doc string for blueprint1."`\n\n- Note: You can\'t send a JSON body with GET method. \n\n## How to install \n`pip install sanic-to-json`\n\n## Contributors\nSee the [GitHub contributor page](https://github.com/kountable/sanic-to-json/graphs/contributors)\n\n\n## License\nsanic-to-json is open source software [licensed as MIT](https://github.com/kountable/sanic-to-json/blob/master/LICENSE).\n\n\n\n',
    'author': 'Cristian Heredia',
    'author_email': 'cheredia@kountable.com',
    'url': 'https://github.com/kountable/sanic-to-json',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['rest_framework_api_key', 'rest_framework_api_key.migrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'djangorestframework-api-key',
    'version': '1.4.1',
    'description': 'API key permissions for the Django REST Framework',
    'long_description': '# Django REST Framework API Key\n\nAPI key permissions for the [Django REST Framework](https://www.django-rest-framework.org).\n\n<div>\n  <a href="https://travis-ci.org/florimondmanca/djangorestframework-api-key">\n      <img src="https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg" alt="build status"/>\n  </a>\n  <a href="https://pypi.org/project/djangorestframework-api-key">\n      <img src="https://badge.fury.io/py/djangorestframework-api-key.svg" alt="package version"/>\n  </a>\n  <a href="https://github.com/ambv/black">\n      <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="code style">\n  </a>\n</div>\n<div>\n  <img src="https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg" alt="python versions"/>\n  <img src="https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b" alt="django versions"/>\n  <img src="https://img.shields.io/badge/drf-3.8+-7f2d2d.svg" alt="drf versions"/>\n</div>\n\n## Introduction\n\n**Django REST Framework API Key is a powerful library for allowing server-side clients to safely use your API.** These clients are typically third-party backends and services (i.e. _machines_) which do not have a user account but still need to interact with your API in a secure way.\n\n### Features\n\n- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.\n- 🔒 **As secure as possible**: API keys are treated with the same level of care than user passwords. They are hashed using the default password hasher before being stored in the database, and only visible at creation.\n- 🎨 **Customizable**: satisfy specific business requirements by building your own customized API key models, permission classes and admin panels.\n\n### Should I use API keys?\n\nThere are important security aspects you need to consider before switching to an API key access control scheme. We\'ve listed some of these in [Security caveats](security.md#caveats), including serving your API over HTTPS.\n\nBesides, see [Why and when to use API keys](https://cloud.google.com/endpoints/docs/openapi/when-why-api-key#top_of_page) for hints on whether API keys can fit your use case.\n\nAPI keys are ideal in the following situations:\n\n- Blocking anonymous traffic.\n- Implementing API key-based [throttling](https://www.django-rest-framework.org/api-guide/throttling/). (Note that Django REST Framework already has may built-in utilities for this use case.)\n- Identifying usage patterns by logging request information along with the API key.\n\nThey can also present enough security for authorizing internal services, such as your API server and an internal frontend application.\n\n> Please note that this package is NOT meant for authentication. You should NOT use this package  to identify individual users, either directly or indirectly.\n>\n> If you need server-to-server authentication, you may want to consider OAuth instead. Libraries such as [django-oauth-toolkit](https://django-oauth-toolkit.readthedocs.io/en/latest/index.html) can help.\n\n## Quickstart\n\nInstall the latest version with `pip`:\n\n```bash\npip install djangorestframework-api-key\n```\n\nAdd the app to your `INSTALLED_APPS`:\n\n```python\n# settings.py\n\nINSTALLED_APPS = [\n  # ...\n  "rest_framework",\n  "rest_framework_api_key",\n]\n```\n\nRun the included migrations:\n\n```bash\npython manage.py migrate\n```\n\nTo learn how to configure permissions and manage API keys, head to the [Documentation](https://florimondmanca.github.io/djangorestframework-api-key).\n\n## Changelog\n\nSee [CHANGELOG.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CHANGELOG.md).\n\n## Contributing\n\nSee [CONTRIBUTING.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CONTRIBUTING.md).\n\n## License\n\nMIT\n',
    'author': 'florimondmanca',
    'author_email': 'florimond.manca@gmail.com',
    'url': 'https://florimondmanca.github.io/djangorestframework-api-key/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

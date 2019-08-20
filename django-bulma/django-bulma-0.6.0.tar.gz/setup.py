# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bulma',
 'bulma.management',
 'bulma.management.commands',
 'bulma.templatetags',
 'bulma.tests']

package_data = \
{'': ['*'],
 'bulma': ['static/bulma/css/*',
           'static/bulma/sass/*',
           'templates/*',
           'templates/_layouts/*',
           'templates/account/*',
           'templates/bulma/*',
           'templates/bulma/forms/*',
           'templates/registration/*']}

setup_kwargs = {
    'name': 'django-bulma',
    'version': '0.6.0',
    'description': 'Bulma CSS Framework for Django projects',
    'long_description': '# A Bulma Theme for Django Projects\n\n<a href="https://github.com/timonweb/django-bulma"><img src="https://raw.githubusercontent.com/timonweb/django-bulma/master/demo/static/images/django-bulma-logo.png" alt="Django Bulma"></a>\n\nA Django base theme based on Bulma (<a href="https://bulma.io/">bulma.io</a>). Bulma is a modern CSS framework based on Flexbox.\n\n*** work in progress ***\n\n## Installation\n\n1. Install the python package django-bulma from pip\n\n  ``pip install django-bulma``\n\n  Alternatively, you can install download or clone this repo and call ``pip install -e .``.\n\n2. Add to INSTALLED_APPS in your **settings.py**:\n\n  `\'bulma\',`\n\n3. If you want to use the provided base template, extend from **bulma/base.html**:\n\n  ```\n  {% extends \'bulma/base.html\' %}\n\n  {% block title %}Bulma Site{% endblock %}\n\n  {% block content %}\n    Content goes here...\n  {% endblock content %}\n\n  ```\n  \n4. If you want to customize bulma sass and your own components:\n\n    4.1 Copy bulma static files into your project\'s **STATIC_ROOT**:\n\n    ```\n    python manage.py copy_bulma_static_into_project\n    ```  \n    You should see **bulma** dir appeared in your **STATIC_ROOT**. It contains\n    three dirs:\n    * **lib** - where we put original and untouched bulma package, in most cases\n    you shouldn\'t mess with it\n    * **sass** - this is the place where you can put your own sass code and customize\n    bulma variables\n    * **css** - this is where compiled sass output goes, you should link this file\n    in your base.html \n\n    4.2 Install npm packages for sass compilation to work:    \n    \n    ```\n    python manage.py bulma install\n    ```\n    \n    4.3 Start sass watch mode:\n    ```\n    python manage.py bulma start\n    ```\n\n5. For forms, in your templates, load the `bulma_tags` library and use the `|bulma` filters:\n\n    ##### Example template\n    \n    ```django\n\n    {% load bulma_tags %}\n\n    {# Display a form #}\n\n    <form action="/url/to/submit/" method="post">\n       {% csrf_token %}\n       {{ form|bulma }}\n       <div class="field">\n         <button type="submit" class="button is-primary">Login</button>\n       </div>\n       <input type="hidden" name="next" value="{{ next }}"/>\n    </form>\n    ```\n\n## Included templates\n\n**django-bulma** comes with:\n* a base template,\n* django core registration templates,\n* django-allauth account templates.\n\n## Bugs and suggestions\n\nIf you have found a bug or if you have a request for additional functionality, please use the issue tracker on GitHub.\n\n[https://github.com/timonweb/django-bulma/issues](https://github.com/timonweb/django-bulma/issues)\n',
    'author': 'Tim Kamanin',
    'author_email': 'tim@timonweb.com',
    'url': 'https://timonweb.com',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

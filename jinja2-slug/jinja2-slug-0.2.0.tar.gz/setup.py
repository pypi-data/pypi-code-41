# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['jinja2_slug']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<3.0', 'unicode-slugify>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'jinja2-slug',
    'version': '0.2.0',
    'description': 'Jinja2 Extension for creating slugs',
    'long_description': None,
    'author': 'Marvin Steadfast',
    'author_email': 'marvin@xsteadfastx.org',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

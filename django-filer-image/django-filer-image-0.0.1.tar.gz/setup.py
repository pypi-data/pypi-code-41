# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_filer_image', 'django_filer_image.migrations']

package_data = \
{'': ['*'], 'django_filer_image': ['jinja2/filer_images/*']}

install_requires = \
['django-filer>=1.5,<2.0',
 'django>=1.11,<3.0',
 'funcy>=1.13,<2.0',
 'pillow>=6.1.0,<7.0.0']

setup_kwargs = {
    'name': 'django-filer-image',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Дмитрий',
    'author_email': 'acrius@mail.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

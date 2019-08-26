# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['rainbow']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rainbow-bridge-logger',
    'version': '0.6.0',
    'description': 'Improved wrapper for native logger of Python 3',
    'long_description': "\n\nRainbow Bridge Logger\n=================================\nA wrapper for the native logging module of Python.\n\n.. code-block:: python\n\n    from rainbow import RainbowLogger\n\n    # __name__ will get the current context\n    # but you can pass any text you want, for identification\n    logger = RainbowLogger(__name__)\n\n    logger.info('my info')\n    logger.warning('my warn')\n    logger.error('my error')\n    logger.debug('my debug')\n",
    'author': 'Almer Mendoza',
    'author_email': 'atmalmer23@gmail.com',
    'url': 'https://github.com/mamerisawesome/rainbow-bridge-logger',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)

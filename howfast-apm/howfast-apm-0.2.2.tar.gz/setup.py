# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['howfast_apm']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

extras_require = \
{'flask': ['flask>=0.8', 'blinker>=1.1']}

setup_kwargs = {
    'name': 'howfast-apm',
    'version': '0.2.2',
    'description': 'Lightweight Application Performance Monitoring middleware that measures and reports performance data to HowFast APM.',
    'long_description': "HowFast APM for Python servers\n==============================\n\nLight instrumentation of your Python server for reporting performance data to `HowFast APM <https://www.howfast.tech/>`_.\n\n.. image:: https://github.com/HowFast/apm-python/blob/master/screenshot.png\n    :align: center\n    :alt: Screenshot from HowFast APM\n\nInstall\n-------\n\nTo install / update the module:\n\n.. code:: bash\n\n    pip install howfast-apm[flask]\n\nUsage\n-------\n\nOnly the Flask middleware is currently available.\n\n.. code:: python\n\n    from howfast_apm import HowFastFlaskMiddleware\n\n    # Create your Flask app\n    app = Flask(__name__, ...)\n\n    # Instanciate all your other middlewares first\n\n    # Setup the APM middleware last, so that it can track the time spent inside other middlewares\n    HowFastFlaskMiddleware(app, app_id=HOWFAST_APM_DSN)\n\nConfiguration\n-------------\n\nYou can configure the APM through environment variables. If they are defined, those variables will\nbe used. Parameters passed to the ``HowFastFlaskMiddleware`` constructor take precedence over environment\nvariables.\n\nOnly one variable is available for now:\n\n* ``HOWFAST_APM_DSN``: The DSN (application identifier) that you can find on your APM dashboard. Can also be passed to the constructor as ``app_id``.\n\nIf the environment variable is defined you can then use:\n\n.. code:: python\n\n    # Install the middleware\n    HowFastFlaskMiddleware(app)\n\nYou can also choose to exclude some URLs from reporting:\n\n.. code:: python\n\n    # Do not report performance data for some URLs\n    HowFastFlaskMiddleware(\n        app,\n        endpoints_blacklist=['/some/internal/url/'],\n    )\n",
    'author': 'Mickaël Bergem',
    'author_email': 'mickael@howfast.tech',
    'url': 'https://github.com/HowFast/apm-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<3.9',
}


setup(**setup_kwargs)

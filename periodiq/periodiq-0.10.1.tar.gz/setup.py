# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['periodiq']
install_requires = \
['dramatiq>=1.5,<2.0', 'pendulum>=2.0,<3.0']

entry_points = \
{'console_scripts': ['periodiq = periodiq:entrypoint']}

setup_kwargs = {
    'name': 'periodiq',
    'version': '0.10.1',
    'description': 'Simple Scheduler for Dramatiq Task Queue',
    'long_description': "# Simple Scheduler for Dramatiq Task Queue\n\n[dramatiq](https://dramatiq.io) task queue is great but lake a scheduler. This\nproject fills the gap.\n\n\n## Features\n\n- Cron-like scheduling.\n- Single process.\n- Fast and simple implementation.\n- Easy on ressources using SIGALRM.\n- No dependency except dramatiq ones.\n- CLI consistent with dramatiq.\n\n\n## Installation\n\nperiodiq is licensed under LGPL 3.0+.\n\n``` console\n$ pip install periodiq\n```\n\nDeclare periodic tasks like this:\n\n``` python\n# filename: app.py\n\nimport dramatiq\nfrom periodiq import PeriodicMiddleWare, cron\n\nbroker.add_middleware(PeriodicMiddleWare())\n\n@dramatiq.actor(periodic=cron('0 * * * *))\ndef hourly():\n    # Do something each hour…\n    ...\n```\n\nThen, run scheduler with:\n\n``` console\n$ periodiq -v app\n```\n\n\n## Support\n\nIf you need help or found a bug, mind [opening a GitLab\nissue](https://gitlab.com/bersace/periodiq/issues/new) on the project. French\nand English spoken.\n",
    'author': 'Étienne BERSAC',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['svtk',
 'svtk.lib',
 'svtk.lib.input_util',
 'svtk.lib.input_util.global_util',
 'svtk.lib.toolbox',
 'svtk.lib.toolbox.test',
 'svtk.vtk_classes']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'svtk',
    'version': '0.1.0',
    'description': 'Streaming Visualization Toolkit',
    'long_description': None,
    'author': 'SimLeek',
    'author_email': 'simulator.leek@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

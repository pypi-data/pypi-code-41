# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hdfdict']

package_data = \
{'': ['*']}

install_requires = \
['h5py-wrapper>=1.1,<2.0', 'pyyaml>=5.1,<6.0']

setup_kwargs = {
    'name': 'hdfdict',
    'version': '0.3.1',
    'description': 'Helps h5py to load and dump dictionaries containing types supported by h5py.',
    'long_description': '# hdfdict helps h5py to dump and load python dictionaries\n\n[![Build Status](https://travis-ci.org/SiggiGue/hdfdict.svg?branch=master)](https://travis-ci.org/SiggiGue/hdfdict)\n\n[![Coverage Status](https://coveralls.io/repos/github/SiggiGue/hdfdict/badge.svg?branch=master)](https://coveralls.io/github/SiggiGue/hdfdict?branch=master)\n\nIf you have a hierarchical data structure of numpy arrays in a dictionary for example, you can use this tool to save this dictionary into a h5py `File()` or `Group()` and load it again.\nThis tool just maps the hdf `Groups` to dict `keys` and the `Datset` to dict `values`.\nOnly types supported by h5py can be used.\nThe dicitonary-keys need to be strings until now.\n\nA lazy loading option is activated per default. So big h5 files are not loaded at once. Instead a dataset gets only loaded if it is accessed from the LazyHdfDict instance.\n\n\n## Example\n\n```python\nimport hdfdict\nimport numpy as np\n\n\nd = {\n    \'a\': np.random.randn(10),\n    \'b\': [1, 2, 3],\n    \'c\': \'Hallo\',\n    \'d\': np.array([\'a\', \'b\']).astype(\'S\'),\n    \'e\': True,\n    \'f\': (True, False),\n}\nfname = \'test_hdfdict.h5\'\nhdfdict.dump(d, fname)\nres = hdfdict.load(fname)\n\nprint(res)\n```\n\nOutput:\n`\n{\'a\': <HDF5 dataset "a": shape (10,), type "<f8">, \'b\': <HDF5 dataset "b": shape (3,), type "<i8">, \'c\': <HDF5 dataset "c": shape (), type "|O">, \'d\': <HDF5 dataset "d": shape (2,), type "|S1">, \'e\': <HDF5 dataset "e": shape (), type "|b1">, \'f\': <HDF5 dataset "f": shape (2,), type "|b1">}\n`\n\nThis are all lazy loding fields in the result `res`.\nJust call `res.unlazy()` or `dict(res)` to get all fields loaded.\nIf you only want to load specific fields, just use item access e.g. `res[\'a\']` so only field \'a\' will be loaded from the file.\n\n\n```python\nprint(dict(res))`\n```\n\nOutput:\n`\n{\'a\': array([-0.47666824,  0.11787749,  0.51405835, -1.49557787, -0.33617182,\n       -0.22381693,  0.25966526,  0.58160661,  0.17019176,  1.3167669 ]), \'b\': array([1, 2, 3]), \'c\': \'Hallo\', \'d\': array([b\'a\', b\'b\'], dtype=\'|S1\'), \'e\': True, \'f\': array([ True, False])}\n`\n\n\n\n\n\n## Installation\n\n+ `pip install hdfdict`\n+ `poetry install hdfdict`\n+ `git clone https://github.com/SiggiGue/hdfdict.git` and `python hdfdict/setup.py install`\n',
    'author': 'Siegfried Gündert',
    'author_email': 'siegfried.guendert@googlemail.com',
    'url': 'https://github.com/SiggiGue/hdfdict',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ezlock']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ezlock',
    'version': '0.1.3',
    'description': 'Super simple file based locking',
    'long_description': '# ezlock\n\nSuper simple file-based locking:\n\n    # first.py\n    from ezlock import Lock\n    import time\n\n    with Lock():\n        print("I got the lock and I\'m keeping it for 20s")\n        time.sleep(20)\n        \n    \nand\n\n    # second.py\n    ...\n    with Lock():\n        print("Trying to get a lock too")\n        \n\nrunning\n\n    >>> python3 first.py &\n    I got the lock and I\'m keeping it for 20s\n    >>> echo "before 20s"\n    before 20s\n    >>> python3 second.py\n    locking.LockError: Attempted to acquire on already locked lock!\n    \nLock files have an owner. A lock can check if it owns a file with `lock.mine`. `Lock`s will only release a lock that\'s not theirs if it\'s forced i.e. `lock.release(force=True)`.\n\nYou can wait for a lock to be released with `Lock.wait()`\n',
    'author': '0Hughman0',
    'author_email': 'rammers2@hotmail.co.uk',
    'url': 'https://github.com/0Hughman0/ezlock',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)

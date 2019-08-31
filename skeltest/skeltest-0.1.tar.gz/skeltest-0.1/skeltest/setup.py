try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'description': 'skeltest',
        'author': 'David Hull',
        'author_email': 'davidhullster@gmail.com',
        'version': '0.1',
        'install_requires': ['nose'],
        'packages': ['skeltest'],
        'scripts': ['/bin/scripts.py'],
        'name': 'skeltest'
    }

setup(**config)

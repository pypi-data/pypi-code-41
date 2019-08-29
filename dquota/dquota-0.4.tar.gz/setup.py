from setuptools import setup
from setuptools import find_packages

setup(
    name = 'dquota',
    version = '0.4',
    author = 'Donatas Abraitis',
    author_email = 'donatas.abraitis@gmail.com',
    description = 'Handle quota notifications using generic netlink',
    url = 'https://github.com/ton31337/dquot-python',
    packages = ['dquota',
                'dquota.providers',
                'dquota.providers.stdout',
                'dquota.providers.redis'
    ],
    install_requires = [
        'pika',
        'redis'
    ]
)


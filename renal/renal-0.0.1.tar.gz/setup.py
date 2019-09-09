from setuptools import setup, Extension
from renal.version import __version__

description = "renal is a command for easily renalaming directories and files."

setup(
    name = 'renal',
    version = __version__,
    description = description,
    long_description = description,
    keywords = 'filesystem bash renalme mv move',
    author = 'Xiaoyong Guo',
    author_email = 'guo.xiaoyong@gmail.com',
    url = 'https://github.com/guoxiaoyong/rena',
    packages = ['renal'],
    package_dir = {"renal": "renal"},
    entry_points = {
        'console_scripts': [
            'renal = renal:main',
        ],
    },
)

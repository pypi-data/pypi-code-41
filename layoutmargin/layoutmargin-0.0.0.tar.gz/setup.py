import os

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


# exposing the params so it can be imported
setup_params = {
    'name': 'layoutmargin',
    # 'version': '20180517',
    'description': 'Mixins that adds margin functionality to Kivy widgets',
    'long_description': read('README.md'),
    'long_description_content_type': 'text/markdown',
    'author': 'Andre Miras',
    'url': 'https://github.com/AndreMiras/garden.layoutmargin',
    'packages': ['layoutmargin'],
    'package_data': {
        'layoutmargin': ['*.kv'],
    },
    'install_requires': [
        'kivy',
    ],
}


def run_setup():
    setup(**setup_params)


# makes sure the setup doesn't run at import time
if __name__ == '__main__':
    run_setup()

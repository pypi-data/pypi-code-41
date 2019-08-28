from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read()
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='danger-noodle',  
    version=version,  
    description='Danger Noodle: Python package manager for npm assets',  
    long_description=long_description,  
    long_description_content_type='text/markdown',  
    url='https://gitlab.com/leopardm/dnd', 
    author='Michael Leopard',  
    author_email='mleopard@gitlab.com',  
    packages=['dnd'],  
    install_requires=requirements,  
    entry_points={  
        'console_scripts': [
            'dnd=dnd.pkg:main',
        ],
    },
)
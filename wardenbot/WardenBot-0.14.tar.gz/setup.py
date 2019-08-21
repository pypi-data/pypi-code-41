import os
from setuptools import setup

# base path
base_path = os.path.dirname(__file__)

# set the long description
with open(os.path.join(base_path, 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# set requirements
with open(os.path.join(base_path, 'requirements.txt')) as r_file:
    REQUIREMENTS = r_file.read().split('\n')

setup(
    name='WardenBot',
    version='0.14',
    packages=['WardenBot'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='WTFPL',
    description='Bot only used for monitoring purpose',
    long_description=README,
    url='https://dadard.fr:3000',
    author='Florian Charpentier',
    author_email='florian.charpentier@epita.fr',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)

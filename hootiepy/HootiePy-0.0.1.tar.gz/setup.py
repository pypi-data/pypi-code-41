from setuptools import setup, find_packages

setup(
    name='HootiePy',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='',
    author='Spencer Porter',
    author_email='spencer.porter3@gmail.com',
    description='A python wrapper for the Hootsuite REST API',
    install_requires=['requests'],
    keywords=['hootsuite', 'sdk', 'oauth', 'api']
)

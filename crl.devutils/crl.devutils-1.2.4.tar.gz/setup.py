import os
import imp
from setuptools import setup, find_packages

__copyright__ = 'Copyright (C) 2019, Nokia'

VERSIONFILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'crl', 'devutils', '_version.py')


def get_version():
    return imp.load_source('_version', VERSIONFILE).get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='crl.devutils',
    version=get_version(),
    author='Petri Huovinen',
    author_email='petri.huovinen@nokia.com',
    description='Common Robot Libraries development and CI tools',
    install_requires=['invoke==0.12.2',
                      'devpi-client==4.1.0',
                      'detox==0.15',
                      'tox==3.4.0',
                      'future',
                      'six',
                      'rstcheck',
                      'sphinx < 1.8.0',
                      'robotframework',
                      'virtualenvrunner',
                      'virtualenv==16.3.0',
                      'configparser'],
    long_description=read('README.rst'),
    license='BSD 3-Clause',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development'],
    keywords='robotframework testing testautomation acceptancetesting atdd bdd',
    url='https://github.com/nokia/crl-devutils',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['crl'],
    entry_points={
        'console_scripts': [
            'crl = crl.devutils.tasks:main']}
)

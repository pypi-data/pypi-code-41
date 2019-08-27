# encoding: utf-8
"""

There is a python client for the Apollo Configuration Center (https://github.com/ctripcorp/apollo) . The original author is filamoon , emial is filamoon@gmail.com. 
Since there is no pypi package, upload it to pypi. If you have any copyright issues, please contact us at momashe@163.com 
"""
from setuptools import setup, find_packages
import pyapollos

SHORT=u'pyapollos'

setup(
    name='pyapollos',
    version=pyapollos.__version__,
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    url='https://github.com/filamoon/pyapollo',
    author=pyapollos.__author__,
    author_email='monashe@163.com',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    package_data={'': ['*.py','*.pyc']},
    zip_safe=False,
    platforms='any',

    description=SHORT,
    long_description=__doc__,
)

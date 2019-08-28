# Conversion from Markdown to pypi's restructured text: https://coderwall.com/p/qawuyq -- Thanks James.

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''
    print('warning: pandoc or pypandoc does not seem to be installed; using empty long_description')

import importlib
from setuptools import setup

install_requires = [x.strip() for x in open('requirements.txt').readlines() if x.strip() and not x.strip().startswith('#')]

setup(
    name='metabltest',
    version=importlib.import_module('bltest').__version__,
    author='Body Labs',
    author_email='aw@bodylabs.com',
    description='BodyLabs unittest extensions',
    long_description=long_description,
    url='https://github.com/bodylabs/___',
    license='MIT',
    packages=[
        'bltest'
    ],
    install_requires=install_requires,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

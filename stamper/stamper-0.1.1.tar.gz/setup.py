import os

from setuptools import setup

version = '0.1.1'

requires = [
    'pygal'
]

setup(
    name='stamper',
    version=version,
    author='Francisco de Borja Lopez Rio',
    author_email='borja@codigo23.net',
    packages=['stamper'],
    url='https://code.codigo23.net/trac/wiki/stamper',
    download_url='http://pypi.python.org/pypi/stamper#downloads',
    license='BSD licence, see LICENSE',
    description='Time tracking tool',
    long_description=open('README.rst').read(),
    scripts=['bin/stamp', 'bin/stamps', 'bin/stamp2json', 'bin/time_sum'],
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        ]
)

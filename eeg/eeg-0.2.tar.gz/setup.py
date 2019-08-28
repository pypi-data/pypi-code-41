import os
from setuptools import setup
#from distutils.core import setup

# with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
#    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='eeg',
    version='0.2',
    packages=['eeg'],

    author='Yeison Cardona',
    author_email='yeisoneng@gmail.com',
    maintainer='Yeison Cardona',
    maintainer_email='yeisoneng@gmail.com',

    # url='http://yeisoncardona.com/',
    download_url='https://bitbucket.org/gcpds/python-eeg/downloads/',

    install_requires=[
        'psutil',
        'openbci',
        'systemd_service',
    ],

    scripts=[
        "cmd/eegstream",
    ],

    # zip_safe=False,

    include_package_data=True,
    license='BSD License',
    description="EEG",
    #    long_description = README,

    classifiers=[

    ],

)

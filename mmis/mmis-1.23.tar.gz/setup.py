#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='mmis',
    version='1.23',
    packages=['mmis'],
    description=['control software for the Modular Microscope Instrument'],
    long_descrioption='README.txt',
    author='Rajeev Bheemireddy TUDelft-DEMO',
    #download_url=['https://homepage.tudelft.nl/6w77j/MMI/MMI.tar.gz'],
    package_data={'mmis':['Images/*.*']},
    #scripts=[''],
    
    )

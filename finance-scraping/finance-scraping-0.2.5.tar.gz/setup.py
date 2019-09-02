import os
from setuptools import setup

__version__ = '0.2.5'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    reqs = f.readlines()

setup(
    name='finance-scraping',
    packages=['finance_scraping'],
    entry_points={
        'console_scripts': ['finance-scraping=finance_scraping.main:main']
    },
    version=__version__,
    description='Finance Scraping ETL Pipeline',
    url='https://github.com/jschnab/finance-scraping',
    author='Jonathan Schnabel',
    author_email='jonathan.schnabel31@gmail.com',
    license='GNU General Public License v3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6.8',
    keywords='security web scraping etl database',
    install_requires=reqs
)

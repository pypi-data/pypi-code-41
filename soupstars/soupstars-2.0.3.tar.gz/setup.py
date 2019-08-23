from setuptools import setup, find_packages
from os import path
from io import open

import soupstars

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='soupstars',
    version=soupstars.__version__,
    description='Declarative web parsers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://soupstars.readthedocs.org',
    author='Tom Waterman',
    author_email='tjwaterman99@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='scraping parsing beautifulsoup beautiful soup',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'beautifulsoup4==4.8.0',
        'requests==2.22',
        'click==7.0'
    ],
    entry_points = {
      'console_scripts': [
          'soupstars = soupstars.cli:cli',
      ],
  }
)

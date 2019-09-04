from setuptools import setup

VERSION = '0.1.0'

setup(
    name='pt_supermarket_scraper',
    version=VERSION,
    py_modules=['pt_supermarket_scraper'],
    url='https://github.com/j38600/pt_supermarket_scraper',
    download_url='https://github.com/j38600/pt_supermarket_scraper/tarball/{}'.format(VERSION),
    license='MIT',
    author='Júlio Sebastião',
    author_email='j38600@gmail.com',
    description='Python library for scraping portuguese supermarkets websites',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['tabulate==0.8.3'],
    entry_points={
        'console_scripts': ['pt_supermarket_scraper=pt_supermarket_scraper:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)
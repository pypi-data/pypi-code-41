import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), "r", encoding='utf-8') as fh:
    LONG_DESCRIPTION = fh.read()

DESCRIPTION = (
    'fix bitmap base on xlwt 1.3.0'
)
CLASSIFIERS = [
    'Programming Language :: Python',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Database',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
]
KEYWORDS = (
    'xls excel workbook worksheet'
)

setup(
    name='xlwt-fixed-bitmap',
    version='1.1.0',
    maintainer='Murray',
    maintainer_email='1063967330@qq.com',
    url='https://github.com/murray88/xlwt-fixed/',
    download_url='https://github.com/murray88/xlwt-fixed/',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='MIT',
    platforms='Platform Independent',
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        'six',
        "xlwt==1.3.0"
    ],
)

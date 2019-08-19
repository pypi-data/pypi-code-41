from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().split()

setup(
    name='pylantern',
    version='0.1.5',
    description='Analytics library',
    long_description=long_description,
    url='https://github.com/timkpaine/lantern',
    download_url='https://github.com/timkpaine/lantern/archive/v0.1.5.tar.gz',
    author='Tim Paine',
    author_email='timothy.k.paine@gmail.com',
    license='Apache 2.0',
    install_requires=requires,
    extras_require={'dev': requires + ['pytest', 'pytest-cov', 'pylint', 'flake8']},

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='analytics tools plotting',

    packages=find_packages(exclude=['tests', ]),
    package_data={'lantern': ['lantern/extensions/hideinput/templates/*',
                              'lantern/extensions/publish/templates/*']},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'nbconvert.exporters': [
            'pdf_hidecode = lantern.extensions.hideinput.exporters:PDFHideCodeExporter',
            'html_hidecode = lantern.extensions.hideinput.exporters:HTMLHideCodeExporter',
        ],
    }
)

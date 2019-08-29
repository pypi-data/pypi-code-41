from setuptools import setup, find_packages
from blockdata import __version__

setup(
    name='blockdata',
    version=__version__,
    author='Kent Kawashima',
    author_email='kentkawashima@gmail.com',
    description='Store coordinate values as a compressed block.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=['block', 'bioinformatics'],
    packages=find_packages(),
)

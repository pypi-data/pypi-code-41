import setuptools
from pathlib import Path

setuptools.setup(
    name='MahidPdf',
    version=1.0,
    long_descripton=Path('README.MD').read_text(),
    packages=setuptools.find_packages(exclude=['TESTS', 'DATA'])
)

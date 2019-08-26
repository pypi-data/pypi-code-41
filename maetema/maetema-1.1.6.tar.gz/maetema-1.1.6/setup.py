from setuptools import setup, find_packages
from distutils.core import Command
import os

VERSION = '1.1.6'


setup(
    name="maetema",
    version=VERSION,
    url='https://docs.maeorg.site',
    license='BSD',
    description='Tema de MaeDocs',
    author='Ham Won Trikru',
    author_email='lwonderlich@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['maeguias>=1.0'],
    python_requires='>=2.7.9,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    entry_points={
        'maeguias.themes': [
            'amelia = maetema.amelia',
            'cerulean = maetema.cerulean',
            'cosmo = maetema.cosmo',
            'cyborg = maetema.cyborg',
            'flatly = maetema.flatly',
            'journal = maetema.journal',
            'readable = maetema.readable',
            'simplex = maetema.simplex',
            'slate = maetema.slate',
            'spacelab = maetema.spacelab',
            'united = maetema.united',
            'yeti = maetema.yeti',
        ]
    },
    zip_safe=False
)

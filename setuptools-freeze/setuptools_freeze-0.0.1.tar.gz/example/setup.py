# -*- coding: utf-8 -*-
from setuptools import setup


if __name__ == '__main__':
    setup(
        name='mypackage',
        version='0.0.1',
        author='AxJu',
        guid='F2AB3B98-C109-4718-BBFF-8EF95824AXXX',
        packages=['mypackage'],
        setup_requires=[
            'setuptools_freeze',
        ],
        entry_points={
            'console_scripts': ['myprogramm=mypackage.gui:main']
        }
    )

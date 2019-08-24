# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.command.install import install


# this is quick and dirty solution to ease multi-name distribution on PyPI
class AbortInstall(install):
    def run(self):
        raise SystemExit(
            "baclang has been renamed to baconlang"
            "Aborting installation."
        )


setup(
    name='baclang',
    version="v1.0.7",
    author='Caleb Martinez',
    author_email='contact@calebmartinez.com',
    description='Renamed package',
    url='https://github.com/baconlang/python',
    include_package_data=True,
    cmdclass={'install': AbortInstall},
    license="BSD",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

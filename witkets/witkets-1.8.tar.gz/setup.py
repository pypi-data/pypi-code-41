import sys
from setuptools import setup, find_packages
from witkets import __version__

long_description = '''Witkets is a collection of extensions for tkinter. 
It comprises a theme applier, a GUI builder and many new widgets, such as: 
LED, Tank, LogicSwitch, NumericLabel, Ribbon, Thermometer and experimental 
Plot and Scope widgets.'''

setup(
    name="witkets",
    version=__version__,
    description="Tkinter extensions",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    author='Leandro Mattioli',
    author_email='leandro.mattioli@gmail.com',
    url='http://www.leandromattioli.com.br/witkets',
    license='LGPL'
)

from setuptools import setup

setup(
    name='smm2sim',
    url='https://github.com/dmparker0/smm2sim/',
    author='Dan Parker',
    author_email='dan.m.parker0@gmail.com',
    packages=['smm2sim'],
    install_requires=['numpy','pandas','scipy','bs4','requests','joblib'],
    version='1.0.2',
    license='MIT',
    description='A tool for simulating the GSA Mario Maker 2 Endless Expert League',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    download_url = 'https://github.com/dmparker0/smm2sim/archive/v1.0.2.tar.gz',
    keywords = ['Mario','SMM','SMM2','GSA','speedrun','simulation','statistics'], 
)

# coding=utf-8
from setuptools import setup

setup(
    name='dmd',
    version='0.1.9',
    packages=['dmd'],
    url='https://gitlab.com/ivarkrabol/dmd',
    license='MIT License',
    author='Ivar H. Kråbøl',
    author_email='dev@ivar.hk',
    description='Basic tools to transform gmbinder-style markdown to gmbinder-style html',
    install_requires=[
        'markdown',
        'click',
        'watchdog',
        'jinja2',
    ],
    scripts=['bin/dmd'],
    include_package_data=True
)

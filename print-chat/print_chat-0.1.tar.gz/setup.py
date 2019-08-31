from setuptools import setup, find_packages
from os.path import join, dirname
import print_chat

setup(
    name='print_chat',
    version=print_chat.__version__,
    packages=find_packages(),
    author='IVIGOR',
    description='Small print tool for implementing chat in the terminal',
    author_email='igor.i.v.a.13@gmail.com',
    url='https://github.com/IVIGOR13/print_chat',
    download_url='https://github.com/IVIGOR13/print_chat/archive/v1.0.tar.gz',
    keywords=['chat', 'terminal'],
    install_requires=['termcolor', 'colorama']
)

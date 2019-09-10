# coding:utf-8
# coding=utf-8
from setuptools import find_packages
from distutils.core import setup
import os
import requests



# 将markdown格式转换为rst格式
def md_to_rst(from_file, to_file):
    r = requests.post(url='http://c.docverter.com/convert',
                      data={'to': 'rst', 'from': 'markdown'},
                      files={'input_files[]': open(from_file, 'rb')})
    if r.ok:
        with open(to_file, "wb") as f:
            f.write(r.content)


md_to_rst("README.md", "README.rst")

if os.path.exists('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'Add a fallback short description here'

if os.path.exists("requirements.txt"):
    install_requires = open("requirements.txt").read().split("\n")
else:
    install_requires = []


setup(
    name='getnum',
    version='1.0.2',
    author='guoyali',
    author_email='840431172@qq.com',
    description='get a num by random',
    maintainer_email='840431172@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    install_requires = install_requires,
    url='https://github.com/guoyali.git',
    # classifiers=[
    #     'Development Status :: 4 - Beta',
    #     'Operating System :: OS Independent',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: BSD License',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: Implementation',
    #     'Programming Language :: Python :: 2',
    #     'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.4',
    #     'Programming Language :: Python :: 3.5',
    #     'Programming Language :: Python :: 3.6',
    #     'Topic :: Software Development :: Libraries'
    # ],

)


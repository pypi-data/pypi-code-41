# coding=utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='ifacetools',
    version="0.1.4",
    description=(
        'A lib created by Vincent for Interface automation test'
    ),
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    author='Vincent',
    author_email='Vincent@163.com',
    maintainer='Vincent',
    maintainer_email='Vincent@163.com',
    license='BSD License',
    # packages=['douban'],
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/huangchunhao/ifacetools',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        #'pymongo',
    ]
)
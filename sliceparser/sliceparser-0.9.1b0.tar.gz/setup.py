import os
from setuptools import setup

_cd = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(_cd, 'README.md')) as infile:
    long_description = infile.read()

setup(
    name='sliceparser',
    packages=['sliceparser'],
    version='0.9.1b',
    license='MIT',
    description='Parse numpy style advanced indexing notation from string.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kaiwen Wu',
    author_email='kps6326@hotmail.com',
    url='https://github.com/kkew3/pysliceparser',
    classifiers=[
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

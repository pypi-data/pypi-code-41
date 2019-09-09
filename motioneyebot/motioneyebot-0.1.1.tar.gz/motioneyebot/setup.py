#! /usr/bin/env python

from setuptools import setup, find_packages, Extension
from setuptools.command.install import install

with open("README.rst", "r") as readme:
    long_desc = readme.read()

setup(
    name='motioneyebot',
    version='69',
    license='MIT',
    author='Ryan Haas',
    author_email='haasrr@etsu.edu',
    description='Use a GroupMe bot to post images from a MotionEyeOS camera, chat with members, and provide weather reports in your GroupMe group.',
    long_description=long_desc,
    long_description_content_type='text/x-rst',
    url='https://github.com/haasr/pops-bot-motioneye',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    entry_points={
        'console_scripts': [
            'motioneyebot=motioneyebot.app:main',
            'motioneyeconfig=motioneyebot.config_util:main'
        ],
    },
    package_data={
        'motioneyebot': ['data/config.txt', 'data/csv_file_license.html', 'data/worldcities.csv']
    },
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=['requests>=2.22.0']
)

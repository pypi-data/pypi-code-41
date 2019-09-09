#! /usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.install import install

with open("README.rst", "r") as readme:
    long_desc = readme.read()

setup(
    name='motioneyebot',
    version='0.1.1',
    license='MIT',
    author='Ryan Haas',
    author_email='haasrr@etsu.edu',
    description='Use a GroupMe bot to post images from a MotionEyeOS camera, chat with members, and provide US weather reports in your GroupMe group.',
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
            'motioneyeconfig=motioneyebot.reconfig_util:main'
        ],
    },
    package_data={
        'motioneyebot': ['data/config.txt',
                        'data/csv_file_license.html',
                        'data/worldcities.csv']
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=['requests>=2.22.0']
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["paho-mqtt","loguru==0.3.2",]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="wenjie wu",
    author_email='wuwenjie718@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="mqtt client for codelab_adapter",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='codelab_adapter_mqtt_client',
    name='codelab_adapter_mqtt_client',
    packages= ['codelab_adapter_mqtt_client','codelab_adapter_mqtt_client.tools'], 
    # packages=find_packages(include=['codelab_adapter_mqtt_client']),
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': [
            'codelab-mqtt-monitor = codelab_adapter_mqtt_client.tools.monitor:monitor',
            'codelab-mqtt-trigger = codelab_adapter_mqtt_client.tools.trigger:trigger'
        ],
    },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/wwj718/codelab_adapter_mqtt_client',
    version='0.2.0',
    zip_safe=False,
)

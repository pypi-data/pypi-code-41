# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-message-plugin",
    version='2.2',
    author='zhen.huang',
    author_email='huangzhen@xinchanedu.com',
    url='https://github.com/a847621843/sentry-message-plugin',
    description='A Sentry extension which send errors stats.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry message plugin',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
        'pytz',
        'django',
    ],
    entry_points={
        'sentry.plugins': [
            'message = message.plugin:MessagePlugin'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ]
)

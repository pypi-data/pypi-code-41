# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_privacy_mgmt import __version__


setup(
    name='django-privacy-mgmt',
    version=__version__,
    description='This package provides a simple interface to provide GDPR-compliant cookie and tracking management on a website.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='what.digital',
    author_email='mario@what.digital',
    packages=find_packages(),
    platforms=['OS Independent'],
    install_requires=[
        'django-parler>=1.8.1',
        'Django>=1.8',
        'django-sekizai>=0.10.0',
    ],
    download_url='https://gitlab.com/what-digital/django-privacy-mgmt/-/archive/{}/django-privacy-mgmt-{}.tar.gz'.format(
        __version__,
        __version__
    ),
    url='https://gitlab.com/what-digital/django-privacy-mgmt/tree/master',
    include_package_data=True,
    zip_safe=False,
)

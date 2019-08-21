import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-google-api',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GPL License',  # example license
    description='a simple app to create workflow and save credentials fro Django',
    long_description=README,
    long_description_content_type='text/x-rst',
    url='https://bitbucket.org/digidiv-pk/django-google-api/src',
    author='Muhammad Usama Bin Liaqat',
    author_email='usama@digidiv.pk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
	   'google-api-python-client>=1.7.11',
	   'google-auth-httplib2>=0.0.3',
	   'google-auth-oauthlib>=0.4.0',
	],
)
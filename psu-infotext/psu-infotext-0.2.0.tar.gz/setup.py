import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='psu-infotext',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    license=None,
    # description='Editable text for Django apps',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/PSU-OIT-ARC/django-psu-infotext',
    author='Mike Gostomski',
    author_email='mjg@pdx.edu',
    classifiers=[
        "Framework :: Django :: 1.11", # 2.2.2
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
    ],
)
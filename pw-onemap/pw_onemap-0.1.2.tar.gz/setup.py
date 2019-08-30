import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
v = open(os.path.join(here, 'VERSION')).readlines()[3]
VERSION = [x.strip().strip("'") for x in v.split('=')][1]

setup(
    name='pw_onemap',
    version='0.1.2',
    packages=find_packages(),
    description='OneMap SG Connector',
    long_description=README,
    author='willy',
    author_email='loh.wilson@gmail.com',
    url='https://gitlab.com/',
    license='MIT',
    install_requires=[
        'requests>=2.19.1',
        'polyline>=1.3.2'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

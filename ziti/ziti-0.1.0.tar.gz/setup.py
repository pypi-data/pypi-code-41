"""install NetFoundry's Ziti module"""

from setuptools import setup

with open("README.txt", "r") as fh:
    long_description = fh.read()

setup(
    name='ziti',
    py_modules=['ziti'],
    author='NetFoundry',
    author_email='support@netfoundry.io',
    url='https://support.netfoundry.io/',
    description='Ziti fabric client for Python programs',
    license='MIT',
    version='0.1.0',
    install_requires=[
        'requests >= 2.18.4',
        'pysocks >= 1.6.7',
        'pyjwt >= 1.6.0'
    ]
)

from setuptools import setup

setup(
    name='cull',
    version='0.16',
    packages=['cull'],
    url='https://pypi.python.org/pypi/cull',
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    author='Travis Edgar',
    author_email='travis.dolan@gmail.com',
    description='A Lasso specific cli parser for AWS output.',
    install_requires=[
        "fire >= 0.1.0",
        "boto3 >= 1.4.4", 'botocore'
    ],
    entry_points={
        'console_scripts': ['cull=cull.cull:main']
    }
)

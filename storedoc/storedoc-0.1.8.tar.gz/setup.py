__version__ = '0.1.8'

from setuptools import setup

from os import path

cwd = path.abspath(path.dirname(__file__))

with open(path.join(cwd, 'README.md'), 'r') as f:
    long_description = f.read()


setup(
    name='storedoc',
    version=__version__,
    description='A python library to upload files on cloud. Supported services - AWS S3, DigitalOcean Spaces, LocalStorage.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rakesh Gunduka',
    author_email='rakesh.gunduka@gmail.com',
    install_requires=['boto3'],
    packages=['storedoc'],
    package_data={},
    license='http://www.opensource.org/licenses/mit-license.php',
    keywords='boto3 aws s3 digitalocean spaces',
    scripts=[
        'storedoc/local.py', 'storedoc/services.py',
        'storedoc/s3.py', 'storedoc/spaces.py'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ]
)

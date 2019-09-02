import codecs
import os

from setuptools import setup, find_packages

from azblobexplorer import __version__

here = os.path.abspath(os.path.dirname(__file__)) + os.sep


def get_requirements(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read().splitlines()


setup(
    name='azblobexplorer',
    version=__version__,
    install_requires=get_requirements('requirements.txt'),
    packages=find_packages(),
    url='https://github.com/akshaybabloo/azure-blob-explorer-python',
    license='MIT',
    author='Akshay Raj Gollahalli',
    author_email='akshay@gollahalli.com',
    description='Download and upload files to Azure Blob storage.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords=['azure', 'secrets'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities'
    ]
)

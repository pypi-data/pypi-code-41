import sys

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.



setup(
    name='functorflow',
    version='2.2.4',
    description='FunctorFlow',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Sam Ravshanov',
    author_email='info@functorflow.org',
	url='http://functorflow.org',
    packages=[''],
    package_data={'': ['*.so', '*.py']},
    zip_safe=False,
    # entry_points={'console_scripts': ['ff = cli:main']},
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
    project_urls={
	    'Home': 'https://functorflow.org/',
        'Blog': 'https://medium.com/functorflow',
	    'Source': 'https://bitbucket.org/functorflow/functorflow-pip'
	},

    install_requires = ['python-dotenv']


)

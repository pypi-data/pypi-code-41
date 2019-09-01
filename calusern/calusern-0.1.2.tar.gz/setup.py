from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='calusern',
    version='0.1.2',
    description=(
        'Transforms https://gitlab.com/cedricvanrompay/annales-brevet-et-bac '
        'into https://cedricvanrompay.gitlab.io/annales-brevet-et-bac'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/cedricvanrompay/calusern',
    author='Cédric Van Rompay',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Education',
        'Topic :: Text Processing :: Markup',
        'Topic :: Documentation',
        'Topic :: Education',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='annales brevet bac examens',
    packages=['calusern'],
    package_data={
        'templates': ['*.html'],
        'static': ['*'],
    },
    python_requires='>=3.6',
    install_requires=['docutils', 'jinja2', 'rst2html5'],
    project_urls={
        'Bug Reports': 'https://gitlab.com/cedricvanrompay/calusern/issues',
    },
)

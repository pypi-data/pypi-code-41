import sys

from setuptools import setup, find_packages

NUMPY_REQUIREMENT = 'numpy>=1.17.2'

PY2 = sys.version_info[0] == 2
PY34 = sys.version_info[0] == 3 and sys.version_info[1] == 4

if PY2 or PY34:
    NUMPY_REQUIREMENT = 'numpy<1.17.0'
elif PY34:
    NUMPY_REQUIREMENT = 'numpy<1.16.0'

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='numpytimebuilder',
    version='0.3.1',
    description='A library for using the NumPy datetime API with aniso8601',
    long_description=README_TEXT,
    author='Brandon Nielsen',
    author_email='nielsenb@jetfuse.net',
    url='https://bitbucket.org/nielsenb/numpytimebuilder',
    install_requires=[
        'aniso8601>=5.0.0, <9.0.0',
        NUMPY_REQUIREMENT
    ],
    packages=find_packages(),
    test_suite='numpytimebuilder',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='iso8601 numpy aniso8601 datetime',
    project_urls={
        'Documentation': 'https://numpytimebuilder.readthedocs.io/',
        'Source': 'https://bitbucket.org/nielsenb/numpytimebuilder',
        'Tracker': 'https://bitbucket.org/nielsenb/numpytimebuilder/issues'
    }
)

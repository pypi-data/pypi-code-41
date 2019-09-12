"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call
from setuptools import Command, find_packages, setup

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=robostash', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='robostash',
    version='0.1.0',
    description='A command-line tool to backup and restore Git Repositories from Atlassian Bitbucket',
    long_description='A command-line tool to backup and restore Git Repositories from Atlassian Bitbucket',
    url='https://github.com/dinohead/robostash',
    author="Derek Halsey",
    author_email='derek@dinohead.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cli',
    packages=find_packages(exclude=['docs', 'tests*']),
    # package_dir={'':''},
    # package_data={ '': ['fonts/*.ttf'], },
    install_requires=['stashy', 'termcolor'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'robostash=robostash.cli:main',
        ],
    },
    cmdclass={'test': RunTests},
)

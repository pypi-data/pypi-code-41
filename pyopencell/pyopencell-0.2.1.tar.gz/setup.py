# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Command
import os
import sys
from shutil import rmtree

with open('README.md') as f:
    README = f.read()


VERSION = '0.2.1'


########
# Copied from https://github.com/kennethreitz/setup.py
here = os.path.abspath(os.path.dirname(__file__))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()
########


setup(
    name='pyopencell',
    version=VERSION,
    author='Coopdevs',
    author_email='info@coopdevs.org',
    maintainer='Daniel Palomar, Antonio Barcia',
    url='https://gitlab.com/coopdevs/pyopencell',
    description='Python wrapper for OpenCell (using REST API)',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests'],
    test_suite='unittest2.collector',
    tests_require=['unittest2', 'mock', 'tox', 'coverage'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Operating System :: POSIX :: Linux',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)

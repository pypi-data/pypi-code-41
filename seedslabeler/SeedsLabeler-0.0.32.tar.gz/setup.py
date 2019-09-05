#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Command
from sys import platform as _platform
from shutil import rmtree
import sys
import os

from src.libs.version import __version__
from src.libs.version import __authors__
from src.libs.version import __authors_username__
from src.libs.version import __author_email__
from src.libs.version import __github__
# print(__version__)

here = os.path.abspath(os.path.dirname(__file__))
NAME = 'SeedsLabeler'
REQUIRES_PYTHON = '>=3.0.0'
REQUIRED_DEP = ['pyqt5', 'lxml', 'numpy', 'pandas', 'requests']

with open('README.md') as readme_file:
    readme = readme_file.read()

# OS specific settings
SET_REQUIRES = []
if _platform == "linux" or _platform == "linux2":
   # linux
   print('linux')
elif _platform == "darwin":
   # MAC OS X
   SET_REQUIRES.append('py2app')

required_packages = find_packages()
required_packages.append('SeedsLabeler')

APP = [NAME + '.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'src/resources/icons/app.icns'
}

class UploadCommand(Command):
    """Support setup.py upload."""

    description=readme + '\n\n',

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
            rmtree(os.path.join(here, 'build'))
            rmtree(os.path.join(here, 'SeedsLabeler.egg-info'))
        except OSError:
            self.status('Fail to remove previous builds..')
            pass

        
        os.system("pyuic5 src/gui/mainwindow.ui -o src/gui/ui_mainwindow.py")

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        # os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git commit -am "minor commit for v{0}"'.format(__version__))
        os.system('git push')
        os.system('git tag -d v{0}'.format(__version__))
        os.system('git tag v{0}'.format(__version__))
        os.system('git push --tags')

        sys.exit()


setup(
    app=APP,
    name=NAME,
    version=__version__,
    description="Seeds annotation tool",
    long_description=readme + '\n\n' ,
    author=__authors__,
    author_email=__author_email__,
    url=__github__,
    python_requires=REQUIRES_PYTHON,
    package_dir={'SeedsLabeler': '.'},
    packages=required_packages,
    entry_points={
        'console_scripts': [
            'SeedsLabeler=SeedsLabeler.SeedsLabeler:main'
        ]
    },
    include_package_data=True,
    install_requires=REQUIRED_DEP,
    license="MIT license",
    zip_safe=False,
    keywords='TCPClient',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    options={'py2app': OPTIONS},
    setup_requires=SET_REQUIRES,
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    }
)

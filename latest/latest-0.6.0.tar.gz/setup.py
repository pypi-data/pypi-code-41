import os.path
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

import latest


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        tox.cmdline(self.test_args)
        sys.exit(1)


setup(
    name=latest.__project__,
    version=latest.__release__,
    description='A LaTeX-oriented template engine.',
    long_description=long_description,
    author='Flavio Grandin',
    author_email='flavio.grandin@gmail.com',
    tests_require=[
        'tox',
    ],
    cmdclass={
        'test': Tox
    },
    install_requires=[
        'pyparsing>=2.2.0',
        'pyyaml>=5.0.0',
    ],
    include_package_data=True,
    license='MIT',
    url='https://github.com/bluephlavio/latest',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
    keywords='latex template engine',
    packages=['latest'],
    entry_points={
        'console_scripts': ['latest=latest.__main__:main'],
    },
)

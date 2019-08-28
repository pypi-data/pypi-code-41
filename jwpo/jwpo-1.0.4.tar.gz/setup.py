from io import open
from setuptools import setup
from setuptools.command.test import test as TestCommand

import jwpo


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        exit(errno)


with open('README.rst', encoding='utf-8') as reader:
    readme = reader.read()

setup(
    name='jwpo',
    version=jwpo.__version__,
    description="Jared Warner's Personalized Opportunities",
    long_description=readme,
    author='Grant Jenks',
    author_email='contact@grantjenks.com',
    url='http://www.grantjenks.com/docs/jwpo/',
    license='Apache 2.0',
    packages=['jwpo'],
    install_requires=['openpyxl'],
    tests_require=['tox'],
    cmdclass={'test': Tox},
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
)

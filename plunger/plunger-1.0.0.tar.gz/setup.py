from setuptools import setup, find_packages
import codecs
import os

version = '1.0.0'


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


long_description = read('README.rst')


setup(
    name='plunger',
    version=version,
    author='Bearstech',
    author_email='py@bearstech.com',
    description="A tool to inspect and clean gitlab's docker registry.",
    long_description=long_description,
    keywords="docker gitlab registry",
    url="https://github.com/factorysh/plunger",
    licence="GPLv3",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Development Status :: 5 - Production/Stable',
    ],
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'sentry-sdk', 'requests', 'pyjwt', 'cryptography', 'texttable',
    ],
    extras_require={
        'test': ['pytest', 'pytest-cov', 'responses'],
    },
    entry_points="""
    [console_scripts]
    plunger = plunger.main:main
    plunger-version = plunger.version:main
    """,
)

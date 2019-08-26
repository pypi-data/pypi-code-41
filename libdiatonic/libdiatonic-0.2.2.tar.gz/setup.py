from setuptools import setup
from imp import find_module, load_module

PROJECT_NAME = 'libdiatonic'
CANONICAL_URL_ROOT = 'https://gitlab.com'
GIT_ORIGIN_USER = 'ajk8'
CANONICAL_URL = '/'.join((CANONICAL_URL_ROOT, GIT_ORIGIN_USER, PROJECT_NAME))

found = find_module('_version', [PROJECT_NAME])
_version = load_module('_version', *found)

setup(
    name=PROJECT_NAME,
    version=_version.__version__,
    description='Library for modeling music theory constructs',
    author='Adam Kaufman',
    author_email='kaufman.blue@gmail.com',
    url=CANONICAL_URL,
    download_url='{}/repository/archive.tar.gz?ref={}'.format(CANONICAL_URL, _version.__version__),
    license='MIT',
    packages=[PROJECT_NAME],
    install_requires=[
        'funcy>=1.7',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='music theory'
)

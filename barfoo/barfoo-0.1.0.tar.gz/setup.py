try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import barfoo

barfoo_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
]

with open('README.rst', 'r') as file:
    barfoo_long_description = file.read()

setup(
    name='barfoo',
    description='Foo bar? No, bar foo!',
    author='Gilberto Agostinho',
    author_email='gilbertohasnofb@gmail.com',
    version=barfoo.__version__,
    packages=find_packages(),
    url='https://github.com/gilbertohasnofb/barfoo',
    license='MIT',
    long_description=barfoo_long_description,
    tests_require=['pytest', 'abjad==3.0.0'],
    classifiers=barfoo_classifiers,
    python_requires='>=3.6',
    install_requires=['abjad==3.0.0'],
)

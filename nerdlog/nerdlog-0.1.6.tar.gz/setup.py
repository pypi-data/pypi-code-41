import nerdlog
from setuptools import setup

long_description = '''NerdLog is a simple logging library, see https://gitlab.com/mhmorgan/pynerdlog'''

setup(
    name='nerdlog',
    version=nerdlog.__version__,
    copyright=nerdlog.__copyright__,
    author=nerdlog.__author__,
    author_email=nerdlog.__author_email__,
    description=nerdlog.__description__,
    long_description=long_description,
    packages=['nerdlog'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)

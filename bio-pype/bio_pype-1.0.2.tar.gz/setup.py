from setuptools import setup
import sys

from pype import __version__

VERSION = __version__.VERSION
DATE = __version__.DATE
AUTHOR = __version__.AUTHOR
MAIL = __version__.MAIL
WEBSITE = __version__.WEBSITE

install_requires = ['PyYAML', 'psutil']

try:
    import argparse
except ImportError:
    install_requires.append('argparse')

setup(
    name='bio_pype',
    version=VERSION,
    description='Management and development framework for bioinformatics pipelines',
    long_description=open('README.rst').read(),
    author=AUTHOR,
    author_email=MAIL,
    url=WEBSITE,
    license='GPLv3',
    packages=['pype', 'pype.modules', 'pype.snippets',
              'pype.profiles', 'pype.pipelines', 'pype.queues',
              'pype.utils'],
    test_suite='test',
    package_data={'pype': ['*.yaml'], 'pype.profiles': ['*.yaml'],
                  'pype.pipelines': ['*.yaml']},
    entry_points={
        'console_scripts': ['pype = pype.commands:main']
    },
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='bioinformatics'
)

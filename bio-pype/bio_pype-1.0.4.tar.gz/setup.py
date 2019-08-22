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

def list_lines(comment):
    for line in comment.strip().split('\n'):
        yield line.strip()

classifier_text = """
    Development Status :: 5 - Production/Stable
    Intended Audience :: Developers
    Intended Audience :: Science/Research
    Intended Audience :: Healthcare Industry
    Intended Audience :: Information Technology
    Operating System :: OS Independent
    License :: OSI Approved :: GNU General Public License v3 (GPLv3)
    Programming Language :: C
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: System :: Distributed Computing 
    Topic :: Utilities
"""

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
    classifiers= list(list_lines(classifier_text)),
    keywords='bioinformatics'
)

#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='DeclaTravaux',
    version='0.1.4',
    description='Utilitaire de transmission de déclarations issues de la plateforme http://www.reseaux-et-canalisations.ineris.fr/',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Pierre Gobin',
    author_email='contact@pierregobin.fr',
    url='https://framagit.org/Pierre86/DeclaTravaux',
    license='CeCILL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business',
        'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    install_requires=[
        'keyring>=10.4.0',
        'PyPDF2>=1.26.0',
        'PyQt5>=5.10',
    ],
    python_requires='>=3.6',
    entry_points={
        'gui_scripts': [
            'DeclaTravaux = DeclaTravaux.__main__:main',
        ],
    },
)

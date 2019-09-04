import os
import os.path
from setuptools import setup
from setuptools import find_packages


def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        return f.read()


setup(
    name='jupyterngsplugin',
    packages=find_packages(),
    data_files=[('', ['README.md'])],
    version='0.0.11a3',
    description='Jupyter notebook plugin for Bioinformatics NGS data analysis',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='Public Domain',
    author='Vera Alvarez, Roberto',
    author_email='veraalva' '@' 'ncbi.nlm.nih.gov',
    maintainer='Vera Alvarez, Roberto',
    maintainer_email='veraalva' '@' 'ncbi.nlm.nih.gov',
    url='https://gitlab.com/r78v10a07/jupyterngsplugin',
    install_requires=['jupyter',
                      'pandas',
                      'wand',
                      'biopython',
                      'xmltodict'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Jupyter',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    keywords='Jupyter NGS',
    project_urls={
        'Documentation': 'https://gitlab.com/r78v10a07/jupyterngsplugin/issues',
        'Source': 'https://gitlab.com/r78v10a07/jupyterngsplugin',
        'Tracker': 'https://gitlab.com/r78v10a07/jupyterngsplugin/issues',
    }
)

from setuptools import setup
import os
import re
import codecs
import sys
import setuptools
from distutils.command.sdist import sdist

# Create new package with python setup.py sdist



here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    print("==========================================",sys.argv)
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cryolo',
    version=find_version("cryolo", "__init__.py"),
    python_requires='>3.4.0',
    packages=['cryolo'],
    url='http://sphire.mpg.de/wiki/doku.php?id=downloads:cryolo_1',
    license='Other/Proprietary License (all rights reserved)',
    author='Thorsten Wagner',
    include_package_data=True,
    package_data={'cryolo': ['../icons/config_icon.png','../icons/program_icon.ico']},
    setup_requires=["Cython"],
    extras_require = {
        'gpu':  ['tensorflow-gpu == 1.10.1','janni[gpu] >= 0.0.5'],
        'cpu': ['tensorflow == 1.10.1', 'janni[cpu] >= 0.0.5']
    },
    install_requires=[
        "mrcfile >= 1.0.0",
        "Cython",
        "Keras >= 2.2.4",
        "numpy == 1.14.5",
        "h5py >= 2.5.0",
        "imageio >= 2.3.0",
        "Pillow >= 6.0.0",
        "tifffile",
        "scipy >= 1.3.0",
        "terminaltables",
        "lineenhancer >= 1.0.6",
        "cryoloBM >= 1.2.6",
        "ansi2html",
        "GooeyDev >= 1.0.3.1"
    ],
    author_email='thorsten.wagner@mpi-dortmund.mpg.de',
    description='Picking procedure for cryo em single particle analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'cryolo_train.py = cryolo.train:_main_',
            'cryolo_predict.py = cryolo.predict:_main_',
            'cryolo_evaluation.py = cryolo.eval:_main_',
            'cryoloo.py = cryolo.cryolo_main:_main_']},
)

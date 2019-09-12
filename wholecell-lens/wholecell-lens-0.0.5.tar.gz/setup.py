import os
import glob
import setuptools
from distutils.core import setup

with open("README.md", 'r') as readme:
    long_description = readme.read()

with open("requirements.txt", 'r') as requirements:
    install_requires = list(requirements.read().splitlines())

setup(
    name='wholecell-lens',
    version='0.0.5',
    packages=['lens'],
    author='Eran Agmon, Ryan Spangler',
    author_email='eagmon@stanford.edu, spanglry@stanford.edu',
    url='https://github.com/CovertLab/Lens',
    license='MIT',
    entry_points={
        'console_scripts': [
            'lens.agent.boot=lens.agent.boot',
            'lens.environment.boot=lens.environment.boot',
            'lens.composites=lens.composites']},
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requires)

#
#  setup.py
#  bxtorch
#
#  Created by Oliver Borchert on May 23, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='BxTorch',
    version='0.5.0',

    author='Oliver Borchert',
    author_email='borchero@in.tum.de',

    description='Large-Scale Machine and Deep Learning in PyTorch.',
    long_description=long_description,
    long_description_content_type = 'text/markdown',

    url='https://github.com/borchero/bxtorch',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    python_requires='>=3.7',
    install_requires=[
        'torch>=1.2.0,<1.3.0',
        'numpy>=1.16.3,<1.17.0',
        'scipy>=1.3.0,<1.4.0',
        'numba>=0.43.1,<0.44.0',
        'scikit-learn>=0.20.3,<0.21.0'
    ],

    license='License :: OSI Approved :: MIT License',
    zip_safe=False
)

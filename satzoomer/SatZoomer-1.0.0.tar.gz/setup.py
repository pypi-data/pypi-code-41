from setuptools import setup
from setuptools import find_packages

long_description = """
Satellite Preprocessing library for BaseMap1
"""

NAME = 'SatZoomer'

requires = ['numpy>=1.9.1',
            'scikit-image',
            'pandas']

classifiers = ['Development Status :: 2 - Pre-Alpha',
                'License :: Other/Proprietary License',
                'Programming Language :: Python :: 3',
                'Operating System :: Microsoft :: Windows',
                'Topic :: Scientific/Engineering :: Visualization']

setup(name=NAME,
        version='1.0.0',
        description='Satellite Image Processing',
        long_description=long_description,
        author='Jacob Rainbow',
        author_email='jacob.rainbow@os.uk',
        url='https://github.com/JRainbowOS/satzoomer',
        install_requires=requires,
        python_requires='>3.6',
        classifiers=classifiers,
        packages=find_packages()
    )

# Needs Python 3.6 due to format strings. This library does not support Python 2.7.
from numpy import get_include as np_include
from setuptools import setup, find_packages, Extension


setup(
    name = 'stsci.image',
    author = 'STScI',
    author_email = 'help@stsci.edu',
    description = 'Image array manipulation functions',
    url = 'https://github.com/spacetelescope/stsci.image',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'numpy>=1.13',
        'scipy',
    ],
    packages = find_packages(),
    package_data = {
        '': ['LICENSE.txt'],
    },
    ext_modules=[
        Extension('stsci.image._combine',
            ['src/_combinemodule.c'],
            include_dirs=[np_include()],
            define_macros=[('NUMPY','1')]),
    ],
    use_scm_version = True,
    setup_requires = ['setuptools_scm'],
)

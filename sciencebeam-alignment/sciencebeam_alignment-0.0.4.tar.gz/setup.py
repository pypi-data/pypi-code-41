from __future__ import print_function

from setuptools import find_packages, setup, Extension

import sciencebeam_alignment


with open('requirements.txt', 'r') as f:
    REQUIRED_PACKAGES = f.readlines()


with open('README.md', 'r') as f:
    long_description = f.read()


NUMPY_REQUIREMENT = [r.rstrip() for r in REQUIRED_PACKAGES if r.startswith('numpy')][0]


def install_numpy_if_not_available():
    try:
        import numpy # noqa pylint: disable=unused-variable
    except ImportError:
        import subprocess
        print('installing numpy:', NUMPY_REQUIREMENT)
        subprocess.check_output(['pip', 'install', NUMPY_REQUIREMENT])


def get_numpy_include_dir():
    install_numpy_if_not_available()

    import numpy as np
    return np.get_include()


packages = find_packages()


setup(
    name='sciencebeam_alignment',
    version=sciencebeam_alignment.__version__,
    install_requires=REQUIRED_PACKAGES,
    packages=packages,
    include_package_data=True,
    description='ScienceBeam Alignment',
    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        'setuptools>=18.0',
        'cython'
    ],
    ext_modules=[
        Extension(
            'sciencebeam_alignment.align_fast_utils',
            sources=['sciencebeam_alignment/align_fast_utils.pyx']
        ),
    ],
    include_dirs=[get_numpy_include_dir()],
    long_description=long_description,
    long_description_content_type='text/markdown'
)

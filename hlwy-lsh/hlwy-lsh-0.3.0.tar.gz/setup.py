#! /usr/bin/env python
from __future__ import print_function

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command, Extension

if "egg_info" in sys.argv:
    USE_CYTHON = False
else:
    # Set this to true to retrigger cpp generation.
    USE_CYTHON = False

DISTNAME = "hlwy-lsh"
DESCRIPTION = "A library for performing shingling and LSH for python."

MAINTAINER = "Matti Lyra"
MAINTAINER_EMAIL = "matti.lyra@gmail.com"
URL = "https://github.com/feynmanlabs/hlwy-lsh"

VERSION = "0.3.0"

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

ext = ".pyx" if USE_CYTHON else ".cpp"
try:
    import numpy as np

    includes = [np.get_include()]
except ImportError:
    includes = []

extensions = [
    Extension(
        "lsh.cMinhash",
        ["lsh/cMinhash{}".format(ext), "lsh/MurmurHash3.cpp"],
        include_dirs=includes,
    )
]
if USE_CYTHON:
    from Cython.Build import cythonize

    extensions = cythonize(extensions)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable)
        )

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


install_deps = ["numpy"]
test_deps = ["coverage>=4.0.3", "pytest>=3.0"]
setup(
    name=DISTNAME,
    version=VERSION,
    description=DESCRIPTION,
    author=MAINTAINER,
    author_email=MAINTAINER_EMAIL,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    packages=["lsh"],
    ext_modules=extensions,
    install_requires=install_deps,
    tests_require=test_deps,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    cmdclass={'upload': UploadCommand},
)

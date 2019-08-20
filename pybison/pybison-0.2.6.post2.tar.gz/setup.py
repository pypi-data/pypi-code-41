"""
Builds bison python module
"""
from __future__ import absolute_import
from __future__ import print_function

import codecs
import sys
import os
from os.path import basename, join, splitext
from glob import glob
from setuptools import find_packages, setup

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


###################################################################
#                             META DATA                           #
###################################################################

NAME = "pybison"
DESCRIPTION='Python bindings for bison/flex parser engine'
VERSION = '0.2.6-2'
URL='https://github.com/lukeparser/pybison'
AUTHOR = 'Lukeparser Team'
LICENSE = 'GPLv2'
PACKAGES = find_packages(where="src")
KEYWORDS = []
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Libraries :: Python Modules'
]
INSTALL_REQUIRES = [
    # "Cython",
    "six",
    "setuptools"
]
SETUP_REQUIRES = [
    # 'Cython'
]
PACKAGE_DATA = [
    "src/bison/c/bison_callback.c",
    "src/bison/c/bison_callback.h",
    "src/bison/c/bisondynlib.h"
]
SCRIPTS = ['utils/bison2py']



###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))



# package_data depending on system
if sys.platform == 'win32':
    libs = []
    extra_link_args = ['/debug', '/Zi']
    bisondynlibModule = 'src/bison/c/bisondynlib-win32.c'
    extra_compile_args = ['/Od', '/Zi', '-D__builtin_expect(a,b)=(a)', '/DCYTHON_TRACE=1']
    for root, dirs, files in os.walk('src/bison/winflexbison'):
        PACKAGE_DATA.extend(join(root.replace('src/bison/', ''), f) for f in files)

elif sys.platform.startswith('linux'):
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []  # ['-DCYTHON_TRACE=1']
    bisondynlibModule = 'src/bison/c/bisondynlib-linux.c'

elif sys.platform.startswith('darwin'):
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []
    bisondynlibModule = 'src/bison/c/bisondynlib-linux.c'
    from distutils import sysconfig
    v = sysconfig.get_config_vars()
    v['LDSHARED'] = v['LDSHARED'].replace('-bundle', '-dynamiclib')

else:
    print('Sorry, your platform is not supported.')
    sys.exit(1)

PACKAGE_DATA.append(bisondynlibModule)




# cython
SOURCES = [
    'src/bison/cython/bison_.pyx',
    'src/bison/c/bison_callback.c',
    bisondynlibModule
]

extra_compile_args = []
extra_link_args = []
define_macros = []

# compile with cython if available
try:
    from Cython.Distutils import build_ext
    from Cython.Distutils.extension import Extension
    cmdclass={'build_ext' : build_ext}
    extension_kwargs={'cython_compile_time_env': {"PY3": sys.version_info.major >= 3}}
except ImportError:
    from distutils.extension import Extension
    print('Cython does not appear to be installed.  Attempting to use pre-made cpp file...')
    cmdclass={}
    extension_kwargs={}
    SOURCES = [s.replace(".pyx",".c") for s in SOURCES]


ext_modules = [
    Extension(
        'bison.bison_',
        sources = SOURCES,
        extra_compile_args=extra_compile_args,
        libraries=libs,
        extra_link_args=extra_link_args,
        **extension_kwargs
    )
]




if __name__ == "__main__":
    setup(
        name=NAME,
        description=DESCRIPTION,
        author=AUTHOR,
        license=LICENSE,
        url=URL,
        version=VERSION,
        keywords=KEYWORDS,
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        setup_requires=SETUP_REQUIRES,

        # from old setup
        cmdclass=cmdclass,
        ext_modules=ext_modules,
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        scripts=SCRIPTS,
        package_data={'bison': PACKAGE_DATA},
    )


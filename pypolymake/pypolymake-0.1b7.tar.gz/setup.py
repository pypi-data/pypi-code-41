# encoding: utf-8
#!/usr/bin/env python
r"""
Installation script for pypolymake

It depends on distutils
"""

from __future__ import print_function

from autogen.pm_types import pm_modules
from setuptools import setup
import distutils
from distutils.cmd import Command
from distutils.command.build_ext import build_ext as _build_ext
from setuptools.extension import Extension

import os
import os.path

DIR = os.path.dirname(__file__)
DEBUG = False

# temporary fix to
#   https://github.com/videlec/pypolymake/issues/17
cfg_vars = distutils.sysconfig.get_config_vars()
cfg_vars['CFLAGS'] = cfg_vars['CFLAGS'].replace("-Wstrict-prototypes", "")


extensions = [
    Extension("polymake.cygmp.utils", ["polymake/cygmp/utils.pyx"]),
    Extension("polymake.pm_object", ["polymake/pm_object.pyx"]),
    Extension("polymake.coercion", ["polymake/coercion.pyx"]),
    Extension("polymake.perl_object", ["polymake/perl_object.pyx"]),
    Extension("polymake.main", ["polymake/main.pyx"]),
    Extension("polymake.handlers", ["polymake/handlers.pyx"]),
    Extension("polymake.big_object", ["polymake/big_object.pyx"]),
#    Extension("polymake.function_dispatcher", ["polymake/function_dispatcher.pyx"],
#        depends = ["polymake/*.pxd", "polymake/cygmp/*"]),
]

for mod in pm_modules():
    extensions.append(Extension("polymake." + mod, ["polymake/" + mod + ".pyx"]))

try:
    import sage.all
    import sage
    import sage.env
    compile_from_sage = True
except ImportError:
    compile_from_sage = False

if compile_from_sage:
    import site
    extensions.append(
        Extension("polymake.sage_conversion", ["polymake/sage_conversion.pyx"]))

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import pytest

        # run the doctests and the tests in the tests/ repo
        sys.exit(pytest.main(["-v", os.path.join(DIR, "tests")]) or
                pytest.main(["--doctest-modules", "-v", os.path.join(DIR, "polymake")]) or
                pytest.main(["--doctest-cython", "-v", os.path.join(DIR, "polymake")]))


# Adapted from Cython's new_build_ext
class build_ext(_build_ext):
    def finalize_options(self):
        # Generate files
        from autogen import rebuild
        rebuild()

        import sys

        # Check dependencies
        try:
            from Cython.Build.Dependencies import cythonize
        except ImportError as E:
            sys.stderr.write("Error: {0}\n".format(E))
            sys.stderr.write("The installation of ppl requires Cython\n")
            sys.exit(1)

        self.distribution.ext_modules[:] = cythonize(
            self.distribution.ext_modules,
            include_path=sys.path,
            gdb_debug=DEBUG)
        _build_ext.finalize_options(self)

def read_file(filename):
    with open(os.path.join(DIR,  filename)) as f:
        return f.read().strip()

setup(
  name = "pypolymake",
  author ="Vincent Delecroix, Burcin Erocal",
  author_email = "sage-devel@googlegroups.com",
  version = read_file('VERSION'),
  description = "Python wrapper for polymake",
  long_description = read_file('README'),
  license = "GNU General Public License, version 3 or later",
  ext_modules = extensions,
  packages = ["polymake", "polymake.cygmp"],
  tests_require=['pytest', 'pytest-cython'],
  package_dir = {"polymake": "polymake",
                 "polymake.cygmp": os.path.join("polymake", "cygmp")},
  package_data = {"polymake": ["*.pxd", "*.pyx", "*.h"],
                  "polymake.cygmp": ["*.pxd", "*.pyx", "*.h"]},
  cmdclass = {'build_ext': build_ext, 'test': TestCommand}
)

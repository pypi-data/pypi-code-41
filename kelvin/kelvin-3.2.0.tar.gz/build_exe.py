#!/bin/env python

"Implements a new distutils 'build_exe' command to build the executable stubs used by Kelvin."

# distutils is a nasty hack.  It hardcodes a lot of assumptions and requires an amazing amount
# of monkey patching to extend.  This project wants to do two simple things:
#
#  1) The build command should build some executables we'll need at runtime.
#  2) The install command should copy the EXEs to the install directory.
#
# To do this, we need to:
#
#   * subclass the Distribution class just to add some attributes (very un-Pythonic design)
#   * write our own build_exe class which duplicates most of build_ext
#   * poke build_exe into the build command using something very ugly

import sys, os, re
from distutils.core import Command, Distribution
from distutils.ccompiler import new_compiler
from distutils import sysconfig
from distutils.ccompiler import CCompiler
from distutils.util import get_platform
from os.path import join

from distutils.command.build import build

# Honestly, how did the distutils "designers" expect people to add subcommands?
def _has_exes(self):
    return bool(getattr(self.distribution, 'exe_modules', 0))
build.sub_commands.append(('build_exe', _has_exes))

assert os.name == 'nt', 'Only Windows is supported at this time.'

# This is practically a duplicate of build_ext, unfortunatley.  This is only used *internally* by Kelvin, which is
# limited to Windows at this time, so this is not full featured.

# The distutils package is a collection of ugly hacks...  Extra keywords to setup are ignored
# if they are not already attributes of Distribution.  Sigh.
#
# To use this, you must use the Distribution2 class which adds an exe_modules attribute to
# Distribution, like ext_modules.  Set this to an array of Executable objects.
#
# To use it, pass "distclass=Distribution2" to the setup function.

class Distribution2(Distribution):
    def __init__ (self, attrs=None):
        self.exe_modules = None
        Distribution.__init__(self, attrs)

class Executable(object):
    def __init__(self, name,
                 subsystem,
                 sources,
                 include_dirs=None,
                 define_macros=None,
                 libraries=None,
                 ):
        self.name          = name
        self.subsystem     = subsystem
        self.sources       = sources
        self.include_dirs  = include_dirs or []
        self.define_macros = define_macros or []
        self.libraries     = libraries or []


class BuildExeCommand(Command):

    description = "builds executable"

    user_options = []

    def __init__(self, dist):
        Command.__init__(self, dist)

    def initialize_options(self):
        self.build_temp = None
        self.build_lib  = None

    def finalize_options(self):
        self.set_undefined_options('build_ext',
                                   ('build_temp', 'build_temp'))

        if not self.build_lib:
            self.build_lib = self._get_build_lib()

    def _get_build_lib(self):
        # More distutils hackishness.  The build.build_lib changes depending on whether
        # ext_modules is empty or not.  For us, obviously it is empty.  Therefore we had to
        # duplicate it.
        return join('build', 'lib.{}-{}'.format(get_platform(), sys.version[0:3]))

    def run(self):

        for exe in self.distribution.exe_modules:

            exe.include_dirs.append(sysconfig.get_python_inc())

            compiler = new_compiler()

            compiler.set_include_dirs(exe.include_dirs)
            for (name, value) in exe.define_macros:
                compiler.define_macro(name, value)

            objects = compiler.compile(exe.sources, output_dir = self.build_temp)

            # This is a hack copied from distutils.commands.build_exe (where it is also called
            # a hack).
            self._build_objects = objects[:]

            print('objects:', objects)

            library_dirs = [ os.path.join(sys.exec_prefix, 'libs') ]
            if sys.base_exec_prefix != sys.prefix:
                # This happens when running in a virtual environment - the libs are not copied
                # on Windows (haven't looked at this on other platforms), so we need to include
                # the original directory.  At least that's what I think is going on.
                library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))

            exe_path = join(self.build_lib, exe.name.split('.')[-1] + '.exe')

            compiler.link(CCompiler.EXECUTABLE,
                          extra_preargs = ['/SUBSYSTEM:{}'.format(exe.subsystem).upper()],
                          objects = objects,
                          output_filename = exe_path,
                          library_dirs = library_dirs,
                          libraries = exe.libraries
                          )

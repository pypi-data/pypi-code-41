# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import os
import subprocess
import sys

try:
    from setuptools import Extension, setup
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.core import Extension, setup
    from distutils.command.build_ext import build_ext

metadata = {}
with open("sq_native/__about__.py", "r") as fp:
    exec(fp.read(), metadata)


# inspired by https://github.com/m-pilia/disptools/blob/d96186cfd5dc5b3a73ec785b0dc443d6e4d9948a/setup.py#L37
class CMakeExtension(Extension):

    def __init__(self, dest_module, cmakelists_dir=".", target=None, options=None, sources=[], **kwa):
        Extension.__init__(self, dest_module, sources=sources, **kwa)
        self.cmakelists_dir = os.path.abspath(cmakelists_dir)
        self.target = target
        self.options = options


class CMakeBuild(build_ext):

    def get_ext_filename(self, name):
        if os.name == "posix" and sys.platform == "darwin":
            ext = ".dylib"
        else:
            ext = ".so"
        return os.path.join(*name.split(".")) + ext

    def build_extensions(self):
        cmake_bin = os.getenv("CMAKE_BIN", "cmake")
        try:
            subprocess.check_output([cmake_bin, "--version"])
        except OSError:
            raise RuntimeError("Cannot find CMake executable")

        for ext in self.extensions:
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            cfg = os.getenv("SQ_NATIVE_BUILD_MODE", "Release")

            cmake_args = [
                "-DCMAKE_BUILD_TYPE=%s" % cfg,
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), extdir),
                "-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), self.build_temp),
            ]

            if ext.options is not None:
                cmake_args.extend(ext.options)

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            # Config and build the extension
            subprocess.check_call([cmake_bin, ext.cmakelists_dir] + cmake_args,
                                  cwd=self.build_temp)
            cmd = [cmake_bin, "--build", ".", "--config", cfg]
            if ext.target is not None:
                cmd.extend(["--target", ext.target])
            subprocess.check_call(cmd, cwd=self.build_temp)


ext_modules = []
root_dir = os.path.dirname(os.path.abspath(__file__))
waf_src = os.path.join(root_dir, "PowerWAF")
if os.path.exists(waf_src):
    ext_modules.append(
        CMakeExtension("sq_native.libSqreen", "PowerWAF", "Sqreen", ["-DKEEP_SYMBOL_FILE=FALSE"]))


setup(
    name="sq-native",
    description="Native module for the Python agent.",
    version=metadata["__version__"],
    author=metadata["__author__"],
    author_email=metadata["__email__"],
    license="proprietary",
    packages=["sq_native"],
    ext_modules=ext_modules,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    cmdclass={"build_ext": CMakeBuild},
    test_suite="tests",
    test_require=["pytest", "mock"],
)

__all__ = [
    'alias', 'bdist_egg', 'bdist_rpm', 'build_ext', 'build_py', 'develop',
    'easy_install', 'egg_info', 'install', 'install_lib', 'rotate', 'saveopts',
    'sdist', 'setopt', 'test', 'install_egg_info', 'install_scripts',
    'register', 'bdist_wininst', 'upload_docs', 'upload', 'build_clib',
    'dist_info',
]

from distutils.command.bdist import bdist
import sys

if "__PEX_UNVENDORED__" in __import__("os").environ:
  from setuptools.command import install_scripts  # vendor:skip
else:
  from pex.third_party.setuptools.command import install_scripts


if 'egg' not in bdist.format_commands:
    bdist.format_command['egg'] = ('bdist_egg', "Python .egg file")
    bdist.format_commands.append('egg')

del bdist, sys

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from contextlib import contextmanager

from _sadmtest.mock.utils.cmd import MockCmdProc
from _sadmtest.mock.utils.path import MockPath
from _sadmtest.mock.utils.sh import MockShUtil

import _sadm.utils.cmd
import _sadm.utils.path
import _sadm.utils.sh

__all__ = ['utils']

def _mockUtils(cfg):
	_sadm.utils.cmd.proc = MockCmdProc(cfg)
	_sadm.utils.path._path = MockPath(cfg)
	_sadm.utils.sh.shutil = MockShUtil(cfg)

def _mockUtilsCheck():
	_sadm.utils.path._path.check()
	_sadm.utils.sh.shutil.check()
	_sadm.utils.cmd.proc.check()

def _mockUtilsRestore():
	_sadm.utils.cmd.proc = _sadm.utils.cmd._ProcMan()
	_sadm.utils.path._path = _sadm.utils.path._Path()
	_sadm.utils.sh.shutil = _sadm.utils.sh._ShUtil()

@contextmanager
def utils(cfg, tag = 'utils'):
	mockcfg = None
	sect = "_sadmtest.mock.%s" % tag
	if cfg and cfg.has_section(sect):
		mockcfg = cfg[sect]
	try:
		_mockUtils(mockcfg)
		yield
		_mockUtilsCheck()
	finally:
		_mockUtilsRestore()

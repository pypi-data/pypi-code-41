# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from os import path
from unittest.mock import Mock

class MockTmpFile(object):
	_fn = None

	def __init__(self, suffix = None, prefix = None, dir = None, remove = False):
		if suffix is None:
			suffix = '.mock'
		if prefix is None:
			prefix = __name__
		if dir is None:
			dir = path.join(path.sep, 'tmp')
		self._fn = path.join(dir, prefix + suffix)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		pass

	def close(self):
		pass

	def unlink(self):
		pass

	def write(self, data):
		pass

	def name(self):
		return self._fn

class MockShUtil(object):
	_mock = None
	_expect = None
	_return = None
	_default = None
	makedirs = None
	chmod = None
	chown = None
	mktmp = None
	getcwd = None
	chdir = None

	def __init__(self, cfg):
		self._expect = []
		self._return = {}
		self._default = {}
		self._mock = Mock()
		self.mktmp = self._mock.mock_mktmp
		self.getcwd = self._mock.mock_getcwd
		self.makedirs = self._mock.mock_makedirs
		self.chmod = self._mock.mock_chmod
		self.chown = self._mock.mock_chown
		self.chdir = self._mock.mock_chdir
		self._configure(cfg)

	def _configure(self, cfg):
		if cfg is None:
			return
		self._utilsDefault()
		self._parseConfig(cfg)
		self.mktmp.side_effect = self._mktmp
		self.getcwd.side_effect = self._sideEffect('getcwd')
		self.makedirs.side_effect = self._sideEffect('makedirs')

	def _utilsDefault(self):
		self._default['getcwd'] = path.join(path.sep, 'testing', 'workdir')

	def _parseConfig(self, cfg):
		data = cfg.get('shutil', fallback = '')
		if data != '':
			for l in data.splitlines():
				l = l.strip()
				if l != '':
					x = l.split(';')
					rtrn = x[0].strip()
					cmdline = ';'.join(x[1:]).strip()
					self._expect.append(cmdline)
					util = cmdline.split(' ')[0].strip()
					self._utilReturn(util, rtrn)

	def _utilReturn(self, name, data):
		if name == '':
			raise RuntimeError('mock shutil: util name is empty')
		if self._return.get(name, None) is None:
			self._return[name] = deque()
		self._return[name].appendleft(data)

	def _sideEffect(self, util):
		def wrapper(*args, **kwargs):
			rtrn = self._return.get(util, None)
			if rtrn is None:
				return self._default.get(util, None)
			try:
				data = rtrn.pop()
			except IndexError:
				return self._default.get(util, None)
			if data == '':
				return self._default.get(util, None)
			return data
		return wrapper

	def _mktmp(self, suffix = None, prefix = None, dir = None, remove = False):
		return MockTmpFile(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

	def check(self):
		got = []
		for x in self._mock.mock_calls:
			xname = x[0].replace('mock_', '', 1)
			xargs = x[1]
			cmdline = xname
			if len(xargs) > 0:
				cmdline = "%s %s" % (xname, ' '.join([str(i) for i in xargs]))
			xkwargs = x[2]
			for k, v in xkwargs.items():
				v = str(v)
				cmdline = "%s, %s=%s" % (cmdline, k, v)
			got.append(cmdline)
		assert got == self._expect, \
			"mock shutil\ngot:\n%s\nexpect:\n%s" % ('\n'.join(got), '\n'.join(self._expect))

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from unittest.mock import Mock

class MockPath(object):
	_mock = None
	_expect = None
	_return = None
	_default = None
	sep = '/'

	def __init__(self, cfg):
		self._expect = []
		self._return = {}
		self._default = {}
		self._mock = Mock()
		self.isfile = self._mock.isfile
		self.isdir = self._mock.isdir
		self.join = self._mock.join
		self.abspath = self._mock.abspath
		self.normpath = self._mock.normpath
		self.unlink = self._mock.unlink
		self._configure(cfg)

	def _configure(self, cfg):
		self._setDefaults()
		self.isfile.side_effect = self._sideEffect('isfile')
		self.isdir.side_effect = self._sideEffect('isdir')
		self.join.side_effect = self._sideEffect('join')
		self.abspath.side_effect = self._sideEffect('abspath')
		self.normpath.side_effect = self._sideEffect('normpath')
		self.unlink.side_effect = self._sideEffect('unlink')
		if cfg is None:
			return
		self._parseConfig(cfg)

	def _setDefaults(self):
		self._default['isfile'] = True
		self._default['isdir'] = True

	def _parseConfig(self, cfg):
		data = cfg.get('path', fallback = '')
		if data != '':
			for l in data.splitlines():
				l = l.strip()
				if l != '':
					x = l.split(';')
					rtrn = x[0].strip()
					cmdline = ';'.join(x[1:]).strip()
					self._expect.append(cmdline)
					util = cmdline.split(' ')[0].strip()
					self._setReturn(util, rtrn)

	def _setReturn(self, name, data):
		if name == '':
			raise RuntimeError('mock path: util name is empty')
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
			if data == 'False':
				return False
			elif data == 'True':
				return True
			return data
		return wrapper

	def check(self):
		got = []
		for x in self._mock.mock_calls:
			xname = x[0]
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
			"mock path got: %s - expect: %s" % (got, self._expect)

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import os
import shutil as _sh
import tempfile

__all__ = ['makedirs', 'chmod', 'chown', 'mktmp', 'getcwd', 'chdir']

class TmpFile(object):
	_fd = None
	_fn = None
	_rm = None

	def __init__(self, suffix = None, prefix = None, dir = None, remove = False):
		if prefix is not None:
			if not prefix.endswith('.'):
				prefix = "%s." % prefix
		self._fd, self._fn = tempfile.mkstemp(suffix = suffix,
			prefix = prefix, dir = dir, text = False)
		self._rm = remove

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.close()
		if self._rm:
			self.unlink()

	def close(self):
		os.close(self._fd)

	def unlink(self):
		os.unlink(self._fn)

	def write(self, data):
		if isinstance(data, str):
			data = data.encode('utf-8')
		os.write(self._fd, data)

	def name(self):
		return self._fn

class _ShUtil(object):
	makedirs = os.makedirs
	chmod = os.chmod
	chown = _sh.chown
	mktmp = None
	getcwd = os.getcwd
	chdir = os.chdir

	def __init__(self):
		self.mktmp = self._mktmp

	def _mktmp(self, suffix = None, prefix = None, dir = None, remove = False):
		return TmpFile(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

shutil = _ShUtil()

def makedirs(name, mode = 0o0755, exists_ok = False):
	return shutil.makedirs(name, mode = mode, exist_ok = exists_ok)

def chmod(path, mode):
	return shutil.chmod(path, mode)

def chown(path, user = None, group = None):
	return shutil.chown(path, user = user, group = group)

def mktmp(suffix = None, prefix = None, dir = None, remove = False):
	return shutil.mktmp(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

def getcwd():
	return shutil.getcwd()

def chdir(path):
	return shutil.chdir(path)

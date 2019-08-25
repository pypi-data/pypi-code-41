# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['TestingProvider']

class TestingProvider(object):

	def auth(self, req, cfg):
		pass

	def repoArgs(self, obj, cfg):
		return {}

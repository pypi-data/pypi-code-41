# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['BitbucketProvider']

class BitbucketProvider(object):

	def auth(self, req, cfg): # FIXME
		pass

	def repoArgs(self, obj, cfg):
		return {
			'repo.path': cfg.get('path'),
		}

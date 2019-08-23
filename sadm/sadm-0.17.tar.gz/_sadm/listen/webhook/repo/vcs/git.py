# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log
from _sadm.utils import sh
from _sadm.utils.cmd import callCheck

__all__ = ['GitRepo']

class GitRepo(object):

	def hook(self, action, args):
		repodir = args.get('repo.path', 'NOREPOPATH')
		log.debug("hook action %s repo dir %s" % (action, repodir))
		sh.chdir(repodir)
		if action == 'push':
			self._pull()
			# TODO: vcs.repo.deploy

	def _pull(self):
		log.debug('git pull')
		callCheck(['git', 'pull'])

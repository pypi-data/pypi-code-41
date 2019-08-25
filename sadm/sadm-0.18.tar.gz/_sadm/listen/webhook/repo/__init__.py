# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json
from json import JSONDecodeError

from _sadm import log
from _sadm.errors import CommandError
from _sadm.listen import wapp
from _sadm.listen.exec import dispatch
from _sadm.listen.errors import error

from .provider.bitbucket import BitbucketProvider

__all__ = ['WebhookRepo']

_validVCS = {
	'git': True,
}
_provider = {
	'bitbucket': BitbucketProvider(),
}

class WebhookRepo(object):
	_cfg = None
	_prov = None
	_provName = None
	_repoName = None
	_repoVCS = None
	_slug = None

	def __init__(self, provider, name):
		self._provName = provider
		self._repoName = name
		self._slug = "%s/%s" % (provider, name)
		prov = _provider.get(provider, None)
		if prov is None:
			raise error(400, "webhook invalid provider: %s" % provider)
		sect = "sadm.webhook:%s" % name
		if not wapp.config.has_section(sect):
			raise error(400, "webhook %s repo not found: %s" % (provider, name))
		self._cfg = wapp.config[sect]
		self._prov = prov
		self._loadProvider(self._cfg, provider, name)
		self._checkRepo(self._cfg)

	def _loadProvider(self, cfg, provider, name):
		rProv = cfg.get('provider', fallback = 'none')
		if rProv != provider:
			raise error(400, "webhook %s: invalid provider: %s" % (self._slug, rProv))

	def _checkRepo(self, cfg):
		vcs = cfg.get('vcs', fallback = 'git')
		if not _validVCS.get(vcs, False):
			raise error(400, "webhook %s: invalid vcs: %s" % (self._slug, vcs))
		self._repoVCS = vcs
		# TODO: check repo.path and other pre-fly checks

	def auth(self, req):
		self._prov.auth(req, self._cfg)

	def exec(self, req, action):
		# TODO: check self._cfg.getboolean(action... if disabled raise error 400
		log.debug("req.body: %s" % req.body)
		if not req.body:
			raise error(400, "webhook %s: no request body" % self._slug)
		try:
			obj = json.loads(req.body.read())
		except JSONDecodeError as err:
			raise error(400, "webhook %s: %s" % (self._slug, err))
		args = self._prov.repoArgs(obj, self._cfg)
		task = "webhook.repo.%s" % self._repoVCS
		try:
			dispatch(req, task, action, args)
		except CommandError as err:
			raise error(500, "webhook %s: %s" % (self._slug, err))

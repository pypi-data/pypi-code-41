# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import request

from _sadm.listen.wapp import wapp, config

from .repo import WebhookRepo

__all__ = ['repo']

@wapp.route('/hook/<provider>/<name>/<action>', 'POST')
def repo(provider, name, action):
	repo = WebhookRepo(config, provider, name)
	repo.auth(request)
	repo.exec(request, action)
	return 'OK\n'

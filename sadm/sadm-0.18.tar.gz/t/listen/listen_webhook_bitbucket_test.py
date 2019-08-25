# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.listen.webhook.handlers import repo

def test_hook_push(listen_wapp):
	with listen_wapp(profile = 'bitbucket') as wapp:
		wapp.POST('bitbucket_push', repo.handle, 'bitbucket', 'testing', 'push')
		assert wapp.response == 'OK'

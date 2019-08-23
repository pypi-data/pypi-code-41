# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import path, systemd

__all__ = ['deploy']

def deploy(env):
	destdir = env.settings.get('network.fail2ban', 'jail.destdir')
	jdisable = env.settings.getlist('network.fail2ban', 'jail.disable')
	for jn in jdisable:
		fn = path.join(destdir, jn + '.conf')
		if path.isfile(fn):
			env.log("remove %s" % fn)
			path.unlink(fn)
	systemd.restart('fail2ban')
	systemd.status('fail2ban')

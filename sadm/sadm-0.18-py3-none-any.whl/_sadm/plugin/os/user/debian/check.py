# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from os import devnull
from pwd import getpwnam

from _sadm.utils.cmd import call

__all__ = ['check']

def check(env):
	diff = deque()
	_checkGroups(diff, env)
	_checkUsers(diff, env)
	return diff

def _checkGroups(diff, env):
	for group in env.settings['os.group']:
		gid = env.settings.getint('os.group', group)
		rc = call("getent group %s >%s" % (group, devnull))
		if rc == 2:
			diff.append(('group', group, gid))
			env.warn("%d %s not found" % (gid, group))
		elif rc == 0:
			env.log("%d %s OK" % (gid, group))
		else:
			raise env.error("getent group command failed: %d" % rc)

def _checkUsers(diff, env):
	for user in env.settings['os.user']:
		uid = env.settings.getint('os.user', user)
		try:
			info = getpwnam(user)
		except KeyError:
			diff.append(('user', user, uid))
			env.warn("%d %s not found" % (uid, user))
		else:
			if info.pw_uid != uid:
				env.warn("%d %s uid %d does not match" % (uid, user, info.pw_uid))
			else:
				env.log("%d %s OK" % (uid, user))

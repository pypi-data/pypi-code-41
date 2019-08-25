# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils.cmd import callCheck
from _sadm.utils.sh import chdir, getcwd

from .check import check

__all__ = ['deploy']

def deploy(env):
	status = check(env)
	for st, name, typ, repo in status:
		if st == 'MISS':
			_cloneRepo(env, name, typ, repo)
		else:
			_updateRepo(env, name, typ, repo)

def _cloneRepo(env, name, typ, repo):
	if typ == 'git':
		_gitClone(env, name, repo)

def _updateRepo(env, name, typ, repo):
	if not repo['update']:
		return
	if typ == 'git':
		_gitUpdate(env, name, repo)

_gitConfigDone = False

def _gitConfig():
	global _gitConfigDone
	cmd = ['git', 'config', '--global', 'core.sshCommand',
		'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no']
	callCheck(cmd)
	_gitConfigDone = True

def _gitClone(env, name, repo):
	_gitConfigDone or _gitConfig()
	env.log("clone git repo %s" % name)
	cmd = ['git', 'clone', '-b', repo['branch'], repo['remote'], repo['path']]
	callCheck(cmd)
	if repo['checkout'] != '':
		oldwd = getcwd()
		try:
			chdir(repo['path'])
			cmd = ['git', 'checkout', repo['checkout']]
			callCheck(cmd)
		finally:
			chdir(oldwd)

def _gitUpdate(env, name, repo):
	env.log("update git repo %s" % name)
	oldwd = getcwd()
	try:
		chdir(repo['path'])
		callCheck(['git', 'pull'])
	finally:
		chdir(oldwd)

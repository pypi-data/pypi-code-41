# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd, path, sh, cmd

__all__ = ['deploy']

def deploy(env):
	systemd.restart('docker')
	for s in env.settings.sections():
		if s.startswith('docker-compose:'):
			name = s.replace('docker-compose:', '', 1).strip()
			cfg = env.settings[s]
			_composeBuild(env, name, cfg)
			_composeConfigure(env, name, cfg)

def _composeBuild(env, name, cfg):
	env.log("docker-compose build %s" % name)
	if cfg.getboolean('build', fallback = True):
		workdir = cfg.get('path')
		oldwdir = sh.getcwd()
		try:
			sh.chdir(workdir)
			cmd.callCheck(['docker-compose', 'build'])
		finally:
			sh.chdir(oldwdir)

def _composeConfigure(env, name, cfg):
	env.log("docker-compose configure %s" % name)
	enable = cfg.getboolean('systemd.enable', fallback = True)
	service = "docker-compose-%s.service" % name
	if enable:
		systemd.enable(service)
		if cfg.getboolean('start', fallback = True):
			systemd.start(service)

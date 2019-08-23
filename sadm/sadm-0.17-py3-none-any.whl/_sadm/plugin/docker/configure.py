# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['configure']

_composeOptions = (
	'enable',
	'path',
	'systemd.enable',
	'build',
	'start',
)

def configure(env, cfg):
	if not cfg.getboolean('docker', 'enable', fallback = False):
		return
	env.settings.merge(cfg, 'docker', ('enable',))
	for s in cfg.sections():
		if s.startswith('docker-compose:'):
			name = s.replace('docker-compose:', '', 1).strip()
			if name == '':
				raise env.error('docker-compose name is empty')
			if cfg.getboolean(s, 'enable', fallback = True):
				env.settings.merge(cfg, s, _composeOptions)

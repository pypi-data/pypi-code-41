# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import version
from _sadm.utils import path

def configure(env, cfg):
	s = env.settings
	s.set('sadm', 'env', env.name())
	s.set('sadm', 'profile', env.profile())
	sess = env.session
	sess.set('sadm.version', version.get())
	_configureDeploy(env, cfg)
	_configureListen(env, cfg)

def _configureDeploy(env, cfg):
	if env.assets.isfile('deploy.cfg'):
		env.log('sync deploy.cfg')
		if not cfg.has_section('sync'):
			cfg.add_section('sync')
		cfg.set('sync', 'sadm.deploy.config',
			"deploy.cfg %s filemode=644" % path.join(path.sep,
				'etc', 'opt', 'sadm', 'deploy.cfg'))

def _configureListen(env, cfg):
	if env.assets.isfile('listen.cfg'):
		env.log('enable sadm.listen')
		env.session.set('sadm.listen.enable', True)
		# sync
		if not cfg.has_section('sync'):
			cfg.add_section('sync')
		cfg.set('sync', 'sadm.listen.config',
			"listen.cfg %s filemode=644" % path.join(path.sep,
				'etc', 'opt', 'sadm', 'listen.cfg'))
		# os.pkg
		if not env.settings.has_section('os.pkg'):
			env.settings.add_section('os.pkg')
		if env.dist() == 'debian':
			env.settings.setlist('os.pkg', 'debian.sadm.listen.install', (
				'at', 'uwsgi-plugin-python3', 'ssl-cert',
			))

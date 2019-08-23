# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle
from configparser import ConfigParser, ExtendedInterpolation

from _sadm import libdir, log, version
from _sadm.listen import errors
from _sadm.utils import path

__all__ = ['wapp', 'config', 'init']

wapp = bottle.Bottle()
bottle.TEMPLATE_PATH = []

_cfgfn = libdir.fpath('listen', 'wapp.conf')
wapp.config.load_config(_cfgfn)

config = ConfigParser(
	defaults = {
		'sadm': {
			'log': 'warn',
		},
		'sadm.listen': {
			'host': '127.0.0.1',
			'port': 3666,
		}
	},
	allow_no_value = False,
	delimiters = ('=',),
	comment_prefixes = ('#',),
	strict = True,
	interpolation = ExtendedInterpolation(),
	default_section = 'default',
)

def init(cfgfn = None):
	if cfgfn is None:
		cfgfn = path.join(path.sep, 'etc', 'opt', 'sadm', 'listen.cfg')
	config.read(cfgfn)

	log.init(config.get('sadm', 'log', fallback = 'warn'))
	log.debug(version.string('sadm'))

	errors.init(wapp)

	from _sadm.listen import handlers
	from _sadm.listen.plugin import HandlersPlugin
	wapp.install(HandlersPlugin())

	initDone = {}
	for sect in config.sections():

		if sect.startswith('sadm.webhook:'):
			if not initDone.get('webhook', False):
				log.debug('enable webhook')
				from _sadm.listen import webhook
				from _sadm.listen.plugin.webhook import WebhookPlugin
				wapp.install(WebhookPlugin())
				initDone['webhook'] = True

	return wapp

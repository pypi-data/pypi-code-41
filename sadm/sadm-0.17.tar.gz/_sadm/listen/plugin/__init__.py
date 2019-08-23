# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import response

from _sadm import log

__all__ = ['HandlersPlugin']

class HandlersPlugin(object):
	api = 2
	name = 'sadm.listen'

	def setup(self, wapp):
		log.debug('setup')

	def apply(self, callback, ctx):
		if ctx.rule.startswith('/_/'):
			log.debug("apply for rule: %s" % ctx.rule)
			def wrapper(*args, **kwargs):
				log.debug('apply.wrapper')
				resp = callback(*args, **kwargs)
				response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
				return resp
			return wrapper
		log.debug("ignore rule: %s" % ctx.rule)
		return callback

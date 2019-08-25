# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle
import json

from io import BytesIO
from os import path

class TestingWebapp(object):
	profile = ''
	name = None
	response = None

	def __init__(self, profile):
		if profile == '':
			self.profile = '.'
		else:
			self.profile = path.join(*profile.split('/'))

	def __postData(self, name):
		fn = path.join('tdata', self.name, self.profile, "%s.json" % name)
		with open(fn, 'r') as fh:
			return json.load(fh)

	def POST(self, pdata, callback, *args):
		post = self.__postData(pdata)
		# TODO: set headers from posdata
		data = json.dumps(post['data']).encode('utf-8')
		bottle.request.environ['CONTENT_LENGTH'] = str(len(data))
		bottle.request.environ['wsgi.input'] = BytesIO()
		bottle.request.environ['wsgi.input'].write(data)
		bottle.request.environ['wsgi.input'].seek(0, 0)
		resp = callback(*args)
		self.response = resp.strip()

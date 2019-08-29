#!/usr/bin/env python3.7

from dataclasses import dataclass, field
from functools import partial
from typing import Any

import requests

__all__ = 'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'bind', 'mount'

@dataclass
class Session():
	"""
	"""
	path: str = None
	endpoint_url: str = None
	session: Any = requests.Session()
	headers: dict = field(default_factory = dict)

	def __post_init__(self):
		self.path = '' if self.path == None else str(self.path)

	def request(self, method, url = '', headers = {}, **kwargs):
		if url == None:
			url = ''
		url = str(url)
		if self.path and not url.startswith('/'):
			url = self.path.rstrip('/') + '/' + url.lstrip('/').rstrip('/')
		if '://' not in url:
			if self.endpoint_url:
				if not url.startswith('/'):
					url = '/' + url
				url = self.endpoint_url + url
		for k, v in self.headers.items():
			headers.setdefault(k, v)
		return self.session.request(method, url, headers = headers, **kwargs)

_attr = f'__{__name__}_sessionmaker__'

def session(obj):
	"""
	"""
	sessionmaker = getattr(obj, _attr)
	return sessionmaker()

def request(obj, url = '', **kwargs):
	"""
	"""
	return session(obj).request(url = url, **kwargs)

get = partial(request, method = 'GET')
post = partial(request, method = 'POST')
put = partial(request, method = 'PUT')
patch = partial(request, method = 'PATCH')
delete = partial(request, method = 'DELETE')
head = partial(request, method = 'HEAD')
options = partial(request, method = 'OPTIONS')


def bind(cls = None, sessionmaker = None, **kwargs):
	"""
	"""
	def wrap(cls):
		nonlocal sessionmaker, kwargs
		if sessionmaker == None:
			def sessionmaker(obj):
				return Session(**{
					k: v(obj) if callable(v) else v
					for k, v in kwargs.items()
				})
		try:
			current_sessionmaker = getattr(cls, _attr)
		except AttributeError:
			return type(cls.__name__, (cls,), {_attr: sessionmaker})
		else:
			def newsessionmaker(obj):
				session = current_sessionmaker(obj)
				session.session = sessionmaker(obj)
				return session
			return type(cls.__name__, (cls,), {_attr: newsessionmaker})
	return wrap(cls) if cls else wrap


def mount(cls, init = True, backref = None, **kwargs):
	"""
	"""
	@property
	def getter(self):
		nonlocal cls, backref
		backref2 = backref
		cls2 = getattr(self, cls) if isinstance(cls, str) else cls
		if backref2:
			if isinstance(backref2, str):
				backref2 = {backref2: self}
			if callable(backref2):
				backref2 = backref2(self)
			cls2 = type(cls2.__name__, (cls2,), backref2)
		cls3 = bind(cls2, session = session(self), **kwargs)
		return cls3() if init else cls3
	return getter

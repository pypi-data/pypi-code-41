from openhltspirent.base import Base
import os
from datetime import datetime


class Openhltest(Base):
	"""This module is the top level of the test hierarchy.
	"""
	YANG_NAME = 'openhltest'
	YANG_KEYWORD = 'module'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = ["authenticate", "set-license-servers"]

	def __init__(self, transport):
		super(Openhltest, self).__init__(transport)

	@property
	def Sessions(self):
		"""A list of test tool sessions.

		Get an instance of the Sessions class.

		Returns:
			obj(openhltspirent.sessions.sessions.Sessions)
		"""
		from openhltspirent.sessions.sessions import Sessions
		return Sessions(self)

	def Authenticate(self, input):
		"""Authenticate a user to the system and return an api-key that can be used to authenticate the user for subsequent requests.
		The api-key can be submitted to the system based on the transport.
		When using the RESTCONF transport the api key is submitted to the system using an http header called X-Api-Key.

		Args:
			input {"username": "string", "password": "string"}

		Returns:
			{"api-key": "string"}

		"""
		ret = self._execute(Base.POST_RPC, 'authenticate', input)
		if isinstance(ret, dict) and 'openhltest:output' in ret: 
			return ret['openhltest:output'] 
		else: 
			return None 

	def SetLicenseServers(self, input):
		"""Provide a list of license servers to the test platform

		Args:
			input {"addresses": "string", "backupserver": "string"}

		"""
		return self._execute(Base.POST_RPC, 'set-license-servers', input)


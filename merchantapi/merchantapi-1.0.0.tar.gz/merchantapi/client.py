"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with self source code.

$Id: client.py 77669 2019-08-29 19:21:04Z gidriss $
"""

import requests
import base64
import hmac
import hashlib
import time
import json

from merchantapi.abstract import Request, Response
from merchantapi.multicall import MultiCallRequest, MultiCallOperation
from requests.exceptions import HTTPError, ConnectionError

'''
Handles sending API requests

:see: https://docs.miva.com/json-api/#authentication
'''


class Client:
	SIGN_DIGEST_NONE = None
	SIGN_DIGEST_SHA1 = 'sha1'
	SIGN_DIGEST_SHA256 = 'sha256'
	DEFAULT_OPTIONS = {
		'require_timestamps': True,
		'signing_key_digest': SIGN_DIGEST_SHA256,
		'default_store_code': None,
		'ssl_verify': True
	}

	def __init__(self, endpoint: str, api_token: str, signing_key: str, options: dict = None):
		self.set_endpoint(endpoint)
		self.set_api_token(api_token)
		self.set_signing_key(signing_key)

		self.options = Client.DEFAULT_OPTIONS.copy()

		if isinstance(options, dict):
			self.options.update(options)

	def get_endpoint(self) -> str:
		"""
		Get the API endpoint URL.

		:returns: str
		"""

		return self.endpoint

	def set_endpoint(self, endpoint: str) -> 'Client':
		"""
		Set the API endpoint URL.

		:param endpoint: str
		:returns: Client
		"""

		self.endpoint = endpoint
		return self

	def get_api_token(self) -> str:
		"""
		Get the api token used to authenticate the request.

		:returns: str
		"""

		return self.api_token

	def set_api_token(self, api_token: str) -> 'Client':
		"""
		Set the api token used to authenticate the request.

		:param api_token: str
		:returns: Client
		"""

		self.api_token = api_token
		return self

	def get_signing_key(self) -> str:
		"""
		Get the signing key used to sign requests. Base64 encoded.

		:returns: str
		"""

		return self.signing_key

	def set_signing_key(self, signing_key: str) -> 'Client':
		"""
		Set the signing key used to sign requests. Base64 encoded.

		:param signing_key: str
		:returns: Client
		"""

		if len(signing_key) % 4 != 0:
			signing_key = signing_key + ('=' * (4 - (len(signing_key) % 4)))

		self.signing_key = signing_key
		return self

	def get_option(self, name: str, default=None):
		"""
		Get a client option.

		:param name: str
		:param default: default return value if not set
		:returns: mixed
		"""

		return self.options[name] if name in self.options else default

	def set_option(self, name: str, value) -> 'Client':
		"""
		Set a client option.

		:param name: str
		:param value: mixed
		:returns: Client
		"""

		if name not in self.options:
			raise Exception('Invalid option %s' % name)
		self.options[name] = value
		return self

	def send(self, request: Request) -> Response:
		"""
		Send a Request object with callback.

		:param request: Request
		:raises Exception:
		:returns: Response
		"""

		default_store = self.get_option('default_store_code')
		response = None

		if isinstance(request, MultiCallRequest):
			for r in request.get_requests():
				if isinstance(r, MultiCallOperation):
					for o in r.get_requests():
						if o.get_scope() == Request.SCOPE_STORE and \
								o.get_store_code() in (None, '') and default_store not in (None, ''):
							o.set_store_code(default_store)
				else:
					if r.get_scope() == Request.SCOPE_STORE and \
							r.get_store_code() in (None, '') and default_store not in (None, ''):
						r.set_store_code(default_store)

			data = request.to_dict()
		else:
			if request.get_scope() == Request.SCOPE_STORE and \
					request.get_store_code() in (None, '') and default_store not in (None, ''):
				request.set_store_code(default_store)

			data = request.to_dict()
			data.update({'Function': request.get_function()})

		if self.get_option('require_timestamps') is True:
			data['Miva_Request_Timestamp'] = int(time.time())

		data = json.dumps(data).encode('utf-8')

		headers = {
			"Content-Type": "application/json",
			"Content-Length": str(len(data)),
			"X-Miva-API-Authorization": self.generate_auth_header(data)
		}

		try:
			response = requests.post(self.endpoint, data=data, headers=headers, verify=self.get_option('ssl_verify'))

			return request.create_response(response.json())
		except ConnectionError as e:
			raise ClientException(request, response, e)
		except HTTPError as e:
			raise ClientException(request, response, e)
		except ValueError as e:
			raise ClientException(request, response, e)

	def generate_auth_header(self, data: str) -> str:
		"""
		Generates the authentication header value.

		:param data: str
		:returns: str
		"""

		hash_type = None
		digest = self.get_option('signing_key_digest')

		if digest is str:
			digest = digest.lower()

		if digest == Client.SIGN_DIGEST_SHA1:
			hash_type = hashlib.sha1
		elif digest == Client.SIGN_DIGEST_SHA256:
			hash_type = hashlib.sha256

		if hash_type is None:
			return 'MIVA %s' % (self.get_api_token())

		key = base64.b64decode(self.get_signing_key())
		result = base64.b64encode(hmac.new(key, data, hash_type).digest())

		return 'MIVA-HMAC-%s %s:%s' % (digest.upper(), self.get_api_token(), result.decode())


'''
ClientException
'''


class ClientException(Exception):
	def __init__(self, request: Request = None, http_response: requests.Response = None, other: Exception = None):
		self.request = request
		self.http_response = http_response
		self.other = other

	def get_request(self) -> Request:
		"""
		Get the Request object being sent
		:return: Request
		"""

		return self.request

	def get_http_response(self) -> requests.Response:
		"""
		Get the Response object of the resulting http request, if available
		:return: requests.Response|None
		"""

		return self.http_response

	def get_other(self) -> Exception:
		"""
		Get the passed Exception, if available
		:return: Exception|None
		"""

		return self.other
